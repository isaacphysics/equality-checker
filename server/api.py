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
from sympy.parsing import sympy_parser
from sympy.printing.latex import latex
from sympy.core.numbers import Integer
import sympy.abc
import sympy
import numpy
import re
#import cPickle
app = Flask(__name__)


KNOWN_PAIRS = dict()


class NumericRangeException(Exception):
    pass


def cleanup_string(string):
    string = re.sub(r'([^0-9])\.([^0-9])', '\g<1> \g<2>', string)  # Allow the . character only surrounded by numbers
    string = string.replace("[", "").replace("]", "")  # This will probably prevent matricies, but good for now
    string = string.replace("'", "").replace('"', '')
    string = string.replace("lambda", "lamda")  # We can't override the built-in keyword
    return string


def known_equal_pair(test_expr, target_expr):
    """In lieu of any real persistent cache of known pairs, just use a dict for now!"""
    pair = (target_expr, test_expr)
    if pair in KNOWN_PAIRS:
        print "Known Pair from %s equality!" % KNOWN_PAIRS[pair]
        return (True, KNOWN_PAIRS[pair])
    else:
        return (False, "known")


def numeric_equality(test_expr, target_expr):
    if len(target_expr.free_symbols) == 0:
        print "No variables in target. Can't be numerically tested."  # Sympy would have caught it if equal
        return False
    if len(test_expr.free_symbols) < len(target_expr.free_symbols):
        print "Not enough variables in test expression. Can't be numerically tested."
        return False
    # Evaluate over a domain, but if the test domain is larger; add in extra dimensions
    domain_target = numpy.random.random_sample((len(target_expr.free_symbols), 10))
    extra_test_freedom = numpy.random.random_sample((len(test_expr.free_symbols) - len(target_expr.free_symbols), 10))
    domain_test = numpy.concatenate((domain_target, extra_test_freedom))

    f_target = sympy.lambdify(target_expr.free_symbols, target_expr, "numpy")
    eval_f_target = f_target(*domain_target)

    f_test = sympy.lambdify(test_expr.free_symbols, test_expr, "numpy")
    eval_f_test = f_test(*domain_test)
    print eval_f_target
    print eval_f_test
    if numpy.max(eval_f_target)-numpy.min(eval_f_target) > 10E10:
        raise NumericRangeException("Error: Too Large Range, numeric equality test unlikely to be accurate!")
    if numpy.max(eval_f_target)-numpy.min(eval_f_target) < 10E-10:
        raise NumericRangeException("Error: Too Small Range, numeric equality test unlikely to be accurate!")
    diff = numpy.sum(numpy.abs(eval_f_target - eval_f_test))
    print "Numeric Equality Tested: difference of %.6E" % diff
    if diff <= (1E-10 * numpy.max(numpy.abs(eval_f_target))):
        print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = "numeric"
        return True
    else:
        return False


def exact_match(test_expr, target_expr):
    if test_expr == target_expr:
        return True


def symbolic_equality(test_expr, target_expr):
    if sympy.simplify(test_expr - target_expr) == 0:
        print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = "symbolic"
        return True


def factorial(n):
    """Stop sympy blindly calculating factorials no matter how large."""
    if type(n) is Integer and n > 50:
        raise NumericRangeException("Too large integer to compute factorial effectively!")
    else:
        return sympy.factorial(n)


@app.route('/check', methods=["POST"])
def check():
    print "\n\n" + "=" * 50
    body = request.get_json(force=True)
    equality_type = ""

    # We may not want implicit_multiplication or split_symbols; that would allow things like L0 or L_0 as variable names, but would require lots of * signs
    # But doing this allows executing of some native python functions!!
    # Say sending "\"=\" * 500000000" will make a really long string.
    # Or "123456789!" will compute this number to arbitrary precision and take a long long time to return . . .
    # Also, doing that currently allows arbitrary functions in ".name()" form to be executed!

#    transforms = sympy_parser.standard_transformations + (sympy_parser.split_symbols, sympy_parser.implicit_multiplication)

    # These two lines fix this somewhat - don't use default import, and whitelist of functions to match:
    transforms = (sympy.parsing.sympy_parser.auto_number, sympy.parsing.sympy_parser.auto_symbol, sympy.parsing.sympy_parser.convert_xor, sympy_parser.split_symbols, sympy_parser.implicit_multiplication)
    global_dict = {"Symbol": sympy.Symbol, "Integer": sympy.Integer, "Float": sympy.Float, "Rational": sympy.Rational,
                   "Mul": sympy.Mul, "Pow": sympy.Pow, "Add": sympy.Add,
                   "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan, "arcsin": sympy.asin, "arccos": sympy.acos, "arctan": sympy.atan,
                   "exp": sympy.exp, "log": sympy.log,
                   "sqrt": sympy.sqrt, "abs": sympy.Abs, "factorial": factorial,
                   "iI": sympy.I, "pi": sympy.pi,
                   "lamda": sympy.abc.lamda}

    if not (("test" in body) and ("target" in body)):
        print "ERROR: Ill-formed request!"
        print body
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    # Prevent splitting of known symbols
    local_dict = {}
    if "symbols" in body:
        for s in str(body["symbols"]).split(","):
            local_dict[s] = sympy.Symbol(s)

    try:
        target_str = cleanup_string(body["target"])
        print target_str
        target_expr = sympy_parser.parse_expr(target_str, transformations=transforms, local_dict=local_dict, global_dict=global_dict, evaluate=False)
        parsedTarget = latex(target_expr)
    except KeyboardInterrupt:#(sympy.parsing.sympy_tokenize.TokenError, SyntaxError, TypeError, AttributeError):
        print "ERROR: TRUSTED EXPRESSION INCORRECTLY FORMATTED!"
        print "Fail: %s" % body["target"]
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    try:
        test_str = cleanup_string(body["test"])
        print test_str
        test_expr = sympy_parser.parse_expr(test_str, transformations=transforms, local_dict=local_dict, global_dict=global_dict, evaluate=False)
        parsedTest = latex(test_expr)
    except KeyboardInterrupt:#(sympy.parsing.sympy_tokenize.TokenError, SyntaxError, TypeError, AttributeError):
        print "Incorrectly formatted ToCheck expression."
        print "Fail: %s" % body["test"]
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    try:
        print "Parsed Target: %s\nParsed ToCheck: %s" % (target_expr, test_expr)

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

    except KeyboardInterrupt:#(SyntaxError, TypeError, AttributeError):
        print "Error when comparing expressions."
        return jsonify(
            target=body["target"],
            test=body["test"],
            parsedTarget=parsedTarget,
            parsedTest=parsedTest,
            error="comparison",
            )
    except NumericRangeException as e:
        print e.message
        equal = False

    print "Equality: %s" % equal
    return jsonify(
        target=body["target"],
        test=body["test"],
        parsedTarget=parsedTarget,
        parsedTest=parsedTest,
        equal=str(equal).lower(),
        equality_type=equality_type
        )


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

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)


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
