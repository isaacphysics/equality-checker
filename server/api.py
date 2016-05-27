# Copyright 2016 James Sharkey
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from sympy.parsing import sympy_parser
from sympy.assumptions.refine import refine, Q
from sympy.core.numbers import Integer, Float, Rational
import sympy.abc
import sympy
import numpy
import re
#import cPickle

__all__ = ["check"]
app = Flask(__name__)


KNOWN_PAIRS = dict()


class NumericRangeException(Exception):
    """An exception to be raised when numeric values are rejected."""
    pass


def cleanup_string(string):
    """Some simple sanity checking and cleanup to perform on passed in strings.

       Since arbitrary strings are passed in, and 'eval' is used implicitly by
       sympy; try and remove the worst offending things from strings.
    """
    string = re.sub(r'([^0-9])\.([^0-9])', '\g<1> \g<2>', string)  # Allow the . character only surrounded by numbers
    string = string.replace("[", "").replace("]", "")  # This will probably prevent matricies, but good for now
    string = string.replace("'", "").replace('"', '')  # We don't need these characters
    string = string.replace("lambda", "lamda").replace("Lambda", "Lamda")  # We can't override the built-in keyword
    string = string.replace("__", " ")  # We don't need double underscores, exploits do
    return string


def known_equal_pair(test_expr, target_expr):
    """In lieu of any real persistent cache of known pairs, just use a dict for now!

       Checks if the two expressions are known pairs from previous testing; this
       should reduce calls to 'simplify' and the numeric testing, both of which
       are computationally costly and slow.
    """
    pair = (target_expr, test_expr)
    if pair in KNOWN_PAIRS:
        print "Known Pair from %s equality!" % KNOWN_PAIRS[pair]
        return (True, KNOWN_PAIRS[pair])
    else:
        return (False, "known")


def parse_expression(expression_str, transforms, local_dict, global_dict):
    """Take a string containing a mathematical expression and return a sympy expression.

       Use sympy's parse_expr(...) function to take the string and convert it to
       a usable format. This presents risks with parsing builtin functions or mathods.
       So apply some transforms to broaden what we can accept, use a dictionary to
       override Python's global namespace, and a local dict of symbols not to split.
        - 'expression_str' should be the string to parse.
        - 'transforms' must be a tuple of sympy transformations.
        - 'local_dict' can be a dictionary of (name, sympy.Symbol(...)) pairs, where
          the string 'name' will not be split up and will be turned into the symbol
          specified. It may be empty.
        - 'global_dict' must be a dictionary mapping string function names to the
          actual functions they will call when evaluated.
    """
    try:
        parsed_expr = sympy_parser.parse_expr(expression_str, transformations=transforms, local_dict=local_dict, global_dict=global_dict, evaluate=False)
        return parsed_expr
    except (sympy.parsing.sympy_tokenize.TokenError, SyntaxError, TypeError, AttributeError, NumericRangeException) as e:
        print "Incorrectly formatted expression."
        print "ERROR: ", e, e.message
        print "Fail: '%s'." % expression_str
        return None


def contains_incorrect_symbols(test_expr, target_expr):
    """Test if the entered expression contains exactly the same symbols as the target.

       Sometimes expressions can be mathematically identical to one another, but
       contain different symbols. From a pure maths standpoint, this is fine; but
       in questions you may not want to allow undefined symbols. This function will
       return a dict containing entries for any extra/missing symbols.
        - 'test_expr' should be the untrusted sympy expression to check symbols from.
        - 'target_expr' should be the trusted sympy expression to match symbols to.
    """
    print "[SYMBOL CHECK]"
    if test_expr.free_symbols != target_expr.free_symbols:
        print "Symbol mismatch between test and target!"
        result = dict()
        missing = ",".join(map(str, (list(target_expr.free_symbols.difference(test_expr.free_symbols)))))
        extra = ",".join(map(str, list(test_expr.free_symbols.difference(target_expr.free_symbols))))
        missing = missing.replace("lamda", "lambda").replace("Lamda", "Lambda")
        extra = extra.replace("lamda", "lambda").replace("Lamda", "Lambda")
        if len(missing) > 0:
            print "Test Expression missing: %s" % missing
            result["missing"] = missing
        if len(extra) > 0:
            print "Test Expression has extra: %s" % extra
            result["extra"] = extra
        return result
    else:
        return None


def exact_match(test_expr, target_expr):
    """Test if the entered expression exactly matches the known expression.

       This equality checking does not expand brackets or perform much simplification,
       so is useful for checking if the submitted answer requires simplifying.
       Testing is first done using '==' which checks that the order of symbols
       matches and will not recognise 'x + 1' as equal to '1 + x'.
       The 'srepr' method outputs sympy's internal representation in a canonical form
       and thus, while performing no simplification, it allows ordering to be ignored
       in exact match checking. These two forms are treated equivalently as 'exact'
       matching.

       Returns True if the sympy expressions have the same internal structure,
       and False if not.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    print "[EXACT TEST]"
    if test_expr == target_expr:
        print "Exact Match (with '==')"
        return True
    elif sympy.srepr(test_expr) == sympy.srepr(target_expr):
        print "Exact Match (with 'srepr')"
        return True
    else:
        return False


def symbolic_equality(test_expr, target_expr):
    """Test if two expressions are symbolically equivalent.

       Use the sympy 'simplify' function to test if the difference between two
       expressions is symbolically zero. This is known to be impossible in the general
       case, but should work well enough for most cases likely to be used on Isaac.
       A return value of 'False' thus does not necessarily mean the two expressions
       are not equal (sympy assumes complex number variables; so some simlifications
       may not occur).

       Returns True if sympy can determine that the two expressions are equal,
       and returns False if this cannot be determined OR if the two expressions
       are definitely not equal.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    print "[SYMBOLIC TEST]"
#    # This would allow assumptions to be made, say to simplify sqrt(x**2) iff x e R and x > 0
#    # Or to expand logarithms and apply the laws of logs (forcing avoids complex number issues)
#    for x in test_expr.free_symbols:
#        test_expr = refine(test_expr, Q.positive(x))  # Probably don't want to actually change
#        test_expr = sympy.expand_log(test_expr, force=True)  # the test expression, but a copy.
    if sympy.simplify(test_expr - target_expr) == 0:
        print "Symbolic match."
        print "Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = "symbolic"
        return True
    else:
        return False


def numeric_equality(test_expr, target_expr):
    """Test if two expressions are numerically equivalent to one another.

       The implementation of this method is liable to change and currently has
       several major flaws. It will sample the test and target functions over
       the free parameters of the target expression. If the test expression has
       more symbols, the parameter space is extended to include these (to test for
       cases where these parameters make no difference).

       Returns True if the two expressions are equal for the sampled points, and
       False otherwise.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    print "[NUMERIC TEST]"
    SAMPLE_POINTS = 25

    # If target has variables not in test, then test cannot possibly be equal.
    # This introduces an asymmetry; target is trusted to only contain necessary symbols,
    # but test is not.
    if len(target_expr.free_symbols.difference(test_expr.free_symbols)) > 0:
        print "Test expression doesn't contain all target expression variables! Can't be numerically tested."
        return False

    # Evaluate over a domain, but if the test domain is larger; add in extra dimensions
    # i.e. if target is f(x) but test is g(x, y) then we need to sample over y too
    # in case it has no effect on the result [say g(x,y) = (y/y) * f(x) , which is
    # mathematically identical to f(x) but may have been missed by the symbolic part.]
    domain_target = numpy.random.random_sample((len(target_expr.free_symbols), SAMPLE_POINTS))
    extra_test_freedom = numpy.random.random_sample((len(test_expr.free_symbols) - len(target_expr.free_symbols), SAMPLE_POINTS))
    domain_test = numpy.concatenate((domain_target, extra_test_freedom))

    # Make sure that the arguments are given in the same order to lambdify for target and test
    # to ensure that when numbers are blindly passed in, the same number goes to the same
    # symbol when evaluated for both test and target.
    shared_variables = list(target_expr.free_symbols)  # We ensured above that all symbols in target are in test also
    extra_test_variables = list(test_expr.free_symbols.difference(target_expr.free_symbols))
    test_variables = shared_variables + extra_test_variables

    # Make the target expression into something numpy can evaluate, then evaluate
    # for the ten points. This *should* now be safe, but still could be dangerous.
    f_target = sympy.lambdify(shared_variables, target_expr, "numpy")
    eval_f_target = f_target(*domain_target)

    # Repeat for the test expression, to get an array of containing SAMPLE_POINTS
    # values of test_expr to be compared to target_expr
    f_test = sympy.lambdify(test_variables, test_expr, "numpy")
    eval_f_test = f_test(*domain_test)

    # Output the function values at the sample points for debugging?
    # The actual domain arrays are probably too long to be worth ever printing.
    print eval_f_target
    print eval_f_test

    # Do some numeric sanity checking; 64-bit floating points are not perfect.
    numeric_range = numpy.abs(numpy.max(eval_f_target)-numpy.min(eval_f_target))
    # If the function is wildly different at these points, probably can't reliably conclude anything
    if numeric_range > 10E10:
        raise NumericRangeException("Error: Too Large Range, numeric equality test unlikely to be accurate!")
    # If the function is the same at all of these points, probably can't conclude anything;
    # Unless the expected result is actually a constant (no free symbols)
    if (numeric_range < 10E-10) and (len(target_expr.free_symbols) > 0):
        raise NumericRangeException("Error: Too Small Range, numeric equality test unlikely to be accurate!")

    # Calculate the difference between the two arrays, if it is less than 10E-8% of
    # the largest value in the target function; the two things are probably equal!
    diff = numpy.sum(numpy.abs(eval_f_target - eval_f_test))
    print "Numeric Equality Tested: difference of %.6E" % diff
    if diff <= (1E-10 * numpy.max(numpy.abs(eval_f_target))):
        print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = "numeric"
        return True
    else:
        return False


def equality(test_expr, target_expr):
    """Given two sympy expressions: test for exact, symbolic and numeric equality.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    # Test each of the three forms of equality:
    equal, equality_type = known_equal_pair(test_expr, target_expr)
    if not equal:
        equality_type = "exact"
        equal = exact_match(test_expr, target_expr)
    if not equal:
        equality_type = "symbolic"
        equal = symbolic_equality(test_expr, target_expr)
    if not equal:
        equality_type = "numeric"
        equal = numeric_equality(test_expr, target_expr)
    return equal, equality_type


def factorial(n):
    """Stop sympy blindly calculating factorials no matter how large.

       If 'n' is a number of some description, ensure that it is smaller than
       a cutoff, otherwise sympy will simply evaluate it, no matter how long that
       may take to complete!
       - 'n' should be a sympy object, that sympy.factorial(...) can use.
    """
    if isinstance(n, (Integer, Float, Rational)) and n > 50:
        raise NumericRangeException("[Factorial]: Too large integer to compute factorial effectively!")
    else:
        return sympy.factorial(n)


def check(test_str, target_str, symbols=None, check_symbols=True, description=None):
    """The main checking function, calls each of the equality checking functions as required.

       Returns a dict describing the equality; with important keys being 'equal',
       and 'equality_type'.

        - 'test_str' should be the untrusted string for sympy to parse.
        - 'target_str' should be the trusted string to parse and match against.
        - 'symbols' should be a comma separated list of symbols not to split.
        - 'check_symbols' indicates whether to verfiy the symbols used in each
           expression are exactly the same or not; setting this to False will
           allow symbols which cancel out to be included (probably don't want this
           in questions).
    """
    # If nothing to parse, fail. On server, this will be caught in check_endpoint()
    if (target_str == "") or (test_str == ""):
        return dict(error="Empty string as argument.")

    print "=" * 50
    # For logging purposes, if we have a description: print it!
    if description is not None:
        print description
        print "=" * 50

    # These two lines address some security issues - don't use default transformations, and whitelist of functions to match.
    # This can't stop some builtin functions, but hopefully removing "." and "[]" will reduce this problem
    transforms = (sympy.parsing.sympy_parser.auto_number, sympy.parsing.sympy_parser.auto_symbol,
                  sympy.parsing.sympy_parser.convert_xor, sympy_parser.split_symbols, sympy_parser.implicit_multiplication)
    global_dict = {"Symbol": sympy.Symbol, "Integer": sympy.Integer, "Float": sympy.Float, "Rational": sympy.Rational,
                   "Mul": sympy.Mul, "Pow": sympy.Pow, "Add": sympy.Add,
                   "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
                   "arcsin": sympy.asin, "arccos": sympy.acos, "arctan": sympy.atan,
                   "sinh": sympy.sinh, "cosh": sympy.cosh, "tanh": sympy.tanh,
                   "sec": sympy.sec, "cosec": sympy.csc, "cot": sympy.cot,
                   "exp": sympy.exp, "log": sympy.log,
                   "sqrt": sympy.sqrt, "abs": sympy.Abs, "factorial": factorial,
                   "iI": sympy.I, "piPI": sympy.pi, "eE": sympy.E,
                   "lamda": sympy.abc.lamda}

    # Prevent splitting of known symbols (symbols with underscores are left alone by default anyway)
    local_dict = {}
    if symbols is not None:
        for s in symbols.split(","):
            local_dict[s] = sympy.Symbol(s)

    # Parse the trusted target expression:
    print "Target string: '%s'" % target_str
    target_expr = parse_expression(target_str, transforms=transforms, local_dict=local_dict, global_dict=global_dict)
    # Parse the untrusted test expression:
    print "Test string: '%s'" % test_str
    test_expr = parse_expression(test_str, transforms=transforms, local_dict=local_dict, global_dict=global_dict)

    if target_expr is None:
        print "ERROR: TRUSTED EXPRESSION CANNOT BE PARSED!"
        print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            error="Parsing Target Expression Failed.",
            )
    if test_expr is None:
        print "Incorrectly formatted ToCheck expression."
        print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            error="Parsing Test Expression Failed.",
            )

    # Now check for symbol match and equality:
    try:
        print "Parsed Target: %s\nParsed ToCheck: %s" % (target_expr, test_expr)
        if check_symbols:  # Do we have same set of symbols in each?
            incorrect_symbols = contains_incorrect_symbols(test_expr, target_expr)
            if incorrect_symbols is not None:
                print "Enforcing strict symbol match for correctness!\nEquality: False"
                print "=" * 50
                return dict(
                    target=target_str,
                    test=test_str,
                    parsedTarget=str(target_expr),
                    parsedTest=str(test_expr),
                    equal=str(False).lower(),
                    equality_type="symbolic",
                    incorrect_symbols=incorrect_symbols,
                )
        # Then check for equality
        equal, equality_type = equality(test_expr, target_expr)
    except (SyntaxError, TypeError, AttributeError, NumericRangeException), e:
        print "Error when comparing expressions: '%s'." % e
        print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            parsedTarget=str(target_expr),
            parsedTest=str(test_expr),
            error="Comparison of expressions failed: '%s'" % e,
            )

    print "Equality: %s" % equal
    print "=" * 50
    return dict(
        target=target_str,
        test=test_str,
        parsedTarget=str(target_expr),
        parsedTest=str(test_expr),
        equal=str(equal).lower(),
        equality_type=equality_type
        )


def make_json_error(ex):
    """Return JSON error pages, not HTML!

       Using a method suggested in http://flask.pocoo.org/snippets/83/, convert
       all outgoing errors into JSON format.
    """
    status_code = ex.code if isinstance(ex, HTTPException) else 500
    response = jsonify(message=str(ex), code=status_code, error=type(ex).__name__)
    response.status_code = (status_code)
    return response


@app.route('/check', methods=["POST"])
def check_endpoint():
    """The route Flask uses to submit things to be checked."""
    body = request.get_json(force=True)

    if not (("test" in body) and ("target" in body)):
        print "ERROR: Ill-formed request!"
        print body
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    # Cleanup the strings before anything is done to them:
    target_str = cleanup_string(body["target"])
    test_str = cleanup_string(body["test"])

    if (target_str == "") or (test_str == ""):
        print "ERROR: Empty string in request!"
        print "Target: '%s'\nTest: '%s'" % (target_str, test_str)
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    if "symbols" in body:
        symbols = str(body["symbols"])
    else:
        symbols = None

    if "check_symbols" in body:
        check_symbols = str(body["check_symbols"]).lower() == "true"
    else:
        check_symbols = True

    if "description" in body:
        description = str(body["description"])
    else:
        description = None

    response_dict = check(test_str, target_str, symbols, check_symbols, description)
    return jsonify(**response_dict)


@app.route('/', methods=["GET"])
def ping():
    return jsonify(code=200)


if __name__ == '__main__':
    # Make sure all outgoing error messages are in JSON format.
    # This will only work provided debug=False - otherwise the debugger hijacks them!
    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error
    # Then run the app
    app.run(port=5000, host="0.0.0.0", debug=False)



##### Some test code to add some form of persistence to cached pairs #####

#@app.route('/save', methods=["POST"])
#def save():
#    print "INFO: Dumping known pairs to file."
#    print KNOWN_PAIRS
#    with open("./KNOWNS.pickle", "a") as f:
#        cPickle.dump(KNOWN_PAIRS, f)
#    return "Saved!"
#
#
#@app.route('/load', methods=["POST"])
#def load():
#    global KNOWN_PAIRS
#    print "INFO: Loading known pairs from file."
#    with open("/equality_checker/KNOWNS.pickle", "a") as f:
#        KNOWN_PAIRS = cPickle.load(f)
#    return "Loaded!"


##### Some test code to implement different limits on the sample space #####

#test = numpy.random.random_sample((4, 10))#numpy.ones((4, 10))
#lims = {"gamma": (0, 0), "b": (0, 0), "c": (0, 1), "d": (0, 0)}
#up_limits = numpy.array([lims[e][1] for e in sorted(lims.keys())])
#low_limits = numpy.array([lims[e][0] for e in sorted(lims.keys())])
#vals = numpy.dot(numpy.diag(up_limits - low_limits), test)
#print vals
#vals += numpy.dot(numpy.diag(low_limits), numpy.ones((4, 10)))
#tttt = sympy_parser.parse_expr("2*lamda+4*c+5*d+3*b", sympy.abc._clash)
#print sorted(tttt.free_symbols, key=lambda x: str(x))
#ffff = sympy.lambdify(sorted(tttt.free_symbols, key=lambda x: str(x)), tttt, "numpy")
#gggg = ffff(*vals)
#print gggg
