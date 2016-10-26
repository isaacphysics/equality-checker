# -*- coding: utf-8 -*-
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
from sympy.core.numbers import Integer, Float, Rational
import sympy.abc
import sympy
import numpy
import re
import signal


__all__ = ["check"]
app = Flask(__name__)


MAX_REQUEST_COMPUTATION_TIME = 5
KNOWN_PAIRS = dict()
RELATIONS_REGEX = '(.*?)(==|<=|>=|<|>)(.*)'
# Numpy (understandably) doesn't have all 24 trig functions defined. Define those missing for completeness. (No hyperbolic inverses for now!)
NUMPY_MISSING_FN = {"csc": lambda x: 1/numpy.sin(x), "sec": lambda x: 1/numpy.cos(x), "cot": lambda x: 1/numpy.tan(x),
                    "acsc": lambda x: numpy.arcsin(numpy.power(x, -1)), "asec": lambda x: numpy.arccos(numpy.power(x, -1)), "acot": lambda x: numpy.arctan(numpy.power(x, -1)),
                    "asinh": lambda x: numpy.arcsinh(x), "acosh": lambda x: numpy.arccosh(x), "atanh": lambda x: numpy.arctanh(x),
                    "csch": lambda x: 1/numpy.sinh(x), "sech": lambda x: 1/numpy.cosh(x), "coth": lambda x: 1/numpy.tanh(x)}
# Make a complex form of the above for no-variable cases of numeric evaluation.
# (Late Binding means that can't just use NUMPY_MISSING_FN[k] since this isn't evaluated in
# the for loop properly. But adding it as a default argument to the lambda *does* cause the
# evaluation and so the two effects cancel out. Neat!)
NUMPY_COMPLEX_FN = {k: lambda x, f=NUMPY_MISSING_FN[k]: f(x + 0j) for k in NUMPY_MISSING_FN.keys()}


class NumericRangeException(Exception):
    """An exception to be raised when numeric values are rejected."""
    pass


class EquationTypeMismatch(TypeError):
    """An exception to be raised when equations are compared to expressions."""
    pass


class TimeoutException(Exception):
    """An exception to be raised if simplification takes too long to finish."""
    pass


class TimeoutProtection:
    """A custom class to abort long-running code.

       The timeout cannot interrupt libraries running external C code, and so
       care must be taken. See http://stackoverflow.com/a/22348885 for source.
       On platforms which do not support SIGALRM (notably Windows), the code will
       run without timeout protection and merely print a warning to the console.
        - 'duration' is the number of seconds to allow the code to run for before
          raising a TimeoutException.
    """
    def __init__(self, duration=10):
        self.duration = duration
        self.timeout_allowed = True
        try:
            signal.SIGALRM
        except AttributeError:
            self.timeout_allowed = False

    def handle_timeout(self, signal_number, frame):
        """The callback function to handle the signal being raised."""
        raise TimeoutException()

    def __enter__(self):
        """Allows a 'with' block. If can set an alarm, do so."""
        if self.timeout_allowed:
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.duration)
        else:
            # We can't use SIGALRM
            print "WARN: Timeout Unsupported!"
            pass

    def __exit__(self, type, value, traceback):
        """Cancels alarm after 'with' block exits."""
        if self.timeout_allowed:
            signal.alarm(0)


class Equal(sympy.Equality):
    """A custom class to override sympy.Equality's str method."""
    def __str__(self):
        """Print the equation in a nice way!"""
        return "%s == %s" % (self.lhs, self.rhs)


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


def cleanup_string(string):
    """Some simple sanity checking and cleanup to perform on passed in strings.

       Since arbitrary strings are passed in, and 'eval' is used implicitly by
       sympy; try and remove the worst offending things from strings.
    """
    # Flask gives us unicode objects anyway, the command line might not!
    if type(string) != unicode:
        string = unicode(string.decode('utf-8'))  # We'll hope it's UTF-8
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
    print "[[KNOWN PAIR CHECK]]"
    pair = (target_expr, test_expr)
    if pair in KNOWN_PAIRS:
        print "Known Pair from %s equality!" % KNOWN_PAIRS[pair]
        return (True, KNOWN_PAIRS[pair])
    else:
        return (False, "known")


def parse_relations(match_object):
    """To ensure that relations like >, >= or == are not evaluated, swap them with Rel class.

       Function to take in a regular expression match from RELATIONS_REGEX and
       replace the string with an actual Relation class from sympy. This is required
       to stop sympy from immediately evaluating all inequalities. It's recursive,
       which should allow nested inequalities - but this functionality may be removed.
        - 'match_object' should be a regex match object matching RELATIONS_REGEX.
    """
    lhs = match_object.group(1).strip()
    relation = match_object.group(2)
    rhs = match_object.group(3).strip()
    if (relation == "=="):
        # Override the default equality relation to use a custom (human-readable) one.
        return "Eq(%s,%s)" % (lhs, rhs)
    else:
        return "Rel(%s,%s,'%s')" % (lhs, rhs, relation)


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
        expression_str = re.sub(RELATIONS_REGEX, parse_relations, expression_str)  # To ensure not evaluated, swap relations with Rel class
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
    print "[[SYMBOL CHECK]]"
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
        print "Not Equal: Enforcing strict symbol match for correctness!"
        return result
    else:
        return None


def eq_type_order(eq_types):
    """Return the worst equality type from a list of equality types.

       Useful for indicating what type of match an equation or relation has: give
       the worst possible type since this is the weakest link in the equality checking.
    """
    if "numeric" in eq_types:
        return "numeric"
    elif "symbolic" in eq_types:
        return "symbolic"
    elif "exact" in eq_types:
        return "exact"
    else:
        raise TypeError("Unexpected list of equality types: %s" % eq_types)


def simplify_derivatives(expr):
    """Simplify all the derivatives in an expression as far as possible.

       Perform simplification of all derivatives in an expression down to the simplest
       possible derivatives, unless they are with respect to more than one variable.
        - 'expr' should be a sympy expression to simplify.
    """
    for derivative in expr.atoms(sympy.Derivative):
        d = simplify_derivative(derivative)
        expr = expr.subs(derivative, d)
    return expr


def simplify_derivative(derivative):
    """Simplify a sympy Derivative object.

       Swap any symbols in a sympy Derivative object into Functions, then do the
       derivative if possible. If the derivative is with respect to more than one
       variable, no simplification is done and the input is returned unchanged.
        - 'derivative' should be a sympy.Derivative object or a TypeError will
          be raised.
    """
    if not derivative.is_Derivative:
        raise TypeError
    d = derivative
    # Get the symbols in the top part of the derivative:
    functions = d.args[0].free_symbols
    # And the variables in the bottom:
    variables = set([sym for t in d.args[1:] for sym in t.free_symbols])
    # Bad things happen if we try simplifying a derivative w.r.t. more than one variable!
    # We won't try and simplify these at all!
    if len(variables) > 1:
        return derivative
    # Remove the variable from the functions list:
    functions = functions.difference(variables)
    # Swap each symbol form of a function to a real function, keeping a way to
    # reverse this process once we've simplified!
    reverse = {}
    for f in functions:
        F = sympy.Function(str(f))(*variables)
        reverse[F] = f
        d = d.subs(f, F)
    # Do any differentiation simplification possible:
    d = d.doit()
    # Undo swapping Symbols to Functions:
    d = d.subs(reverse)
    # Then for logging print the simplification:
    if derivative != d:
        print "Simplified '%s' to '%s'!" % (derivative, d)
    return d


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
    # Here we make the assumption that all variables are real and positive to
    # aid the simplification process. Since we do this for numeric checking anyway,
    # it doesn't seem like much of an issue. Removing 'sympy.posify()' below will
    # stop this.
    try:
        if sympy.simplify(sympy.posify(test_expr - target_expr)[0]) == 0:
            print "Symbolic match."
            print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
            KNOWN_PAIRS[(target_expr, test_expr)] = "symbolic"
            return True
        else:
            return False
    except NotImplementedError, e:
        print "%s: %s - Can't check symbolic equality!" % (type(e).__name__, e.message.capitalize())
        return False


def numeric_equality(test_expr, target_expr, complexify=False):
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
        - 'complexify' is a boolean flag for sampling in the complex plane rather
          than just over the reals.
    """
    print "[NUMERIC TEST]" if not complexify else "[NUMERIC TEST (COMPLEX)]"
    SAMPLE_POINTS = 25
    lambdify_modules = [NUMPY_MISSING_FN, "numpy"]

    # Leave original expressions unchanged!
    target_expr_n = target_expr
    test_expr_n = test_expr

    # Replace any derivatives that exist with new dummy symbols, and treat them
    # as independent from the variables they involve. To avoid naming clashes,
    # just name them in ascending numeric order.
    for d, derivative in enumerate(target_expr.atoms(sympy.Derivative).union(test_expr.atoms(sympy.Derivative))):
        derivative_symbol = sympy.Symbol("Derivative_%s" % d)
        print "Swapping '%s' into variable '%s' for numeric evaluation!" % (derivative, derivative_symbol)
        target_expr_n = target_expr_n.subs(derivative, derivative_symbol)
        test_expr_n = test_expr_n.subs(derivative, derivative_symbol)

    # If target has variables not in test, then test cannot possibly be equal.
    # This introduces an asymmetry; target is trusted to only contain necessary symbols,
    # but test is not.
    if len(target_expr_n.free_symbols.difference(test_expr_n.free_symbols)) > 0:
        print "Test expression doesn't contain all target expression variables! Can't be numerically tested."
        return False

    # Evaluate over a domain, but if the test domain is larger; add in extra dimensions
    # i.e. if target is f(x) but test is g(x, y) then we need to sample over y too
    # in case it has no effect on the result [say g(x,y) = (y/y) * f(x) , which is
    # mathematically identical to f(x) but may have been missed by the symbolic part.]
    domain_target = numpy.random.random_sample((len(target_expr_n.free_symbols), SAMPLE_POINTS))
    extra_test_freedom = numpy.random.random_sample((len(test_expr_n.free_symbols) - len(target_expr_n.free_symbols), SAMPLE_POINTS))
    domain_test = numpy.concatenate((domain_target, extra_test_freedom))

    # If we're trying the samples in the complex plane, make these arrays complex
    # in the simplest way possible: adding 0 of the imaginary unit.
    # Also use the complex versions of the missing numpy functions (for cases
    # where there are no variables, only constants, this is essential!)
    if complexify:
        domain_target = domain_target + 0j
        domain_test = domain_test + 0j
        lambdify_modules = [NUMPY_COMPLEX_FN, "numpy"]

    # Make sure that the arguments are given in the same order to lambdify for target and test
    # to ensure that when numbers are blindly passed in, the same number goes to the same
    # symbol when evaluated for both test and target.
    shared_variables = list(target_expr_n.free_symbols)  # We ensured above that all symbols in target are in test also
    extra_test_variables = list(test_expr_n.free_symbols.difference(target_expr_n.free_symbols))
    test_variables = shared_variables + extra_test_variables

    # Make the target expression into something numpy can evaluate, then evaluate
    # for the ten points. This *should* now be safe, but still could be dangerous.
    f_target = sympy.lambdify(shared_variables, target_expr_n, lambdify_modules)
    eval_f_target = f_target(*domain_target)

    # Repeat for the test expression, to get an array of containing SAMPLE_POINTS
    # values of test_expr_n to be compared to target_expr_n
    f_test = sympy.lambdify(test_variables, test_expr_n, lambdify_modules)
    eval_f_test = f_test(*domain_test)

    # Output the function values at the sample points for debugging?
    # The actual domain arrays are probably too long to be worth ever printing.
    print "Target function value(s):"
    print eval_f_target
    print "Test function value(s):"
    print eval_f_test

    # If get any NaN's from the functions; things are looking bad:
    if numpy.any(numpy.isnan(eval_f_target)) or numpy.any(numpy.isnan(eval_f_test)):
        # If have not tried using complex numbers, try using those:
        if not complexify:
            print "A function appears to be undefined in the interval [0,1). Trying again with complex values!"
            return numeric_equality(test_expr, target_expr, complexify=True)
        else:
            # If have tried using complex numbers, can't evaluate and have gone badly wrong:
            raise NumericRangeException("A function in the test or target expression is undefined in the interval [0,1).")

    # Do some numeric sanity checking; 64-bit floating points are not perfect.
    numeric_range = numpy.abs(numpy.max(eval_f_target)-numpy.min(eval_f_target))
    # If the function is wildly different at these points, probably can't reliably conclude anything
    if numeric_range > 10E10:
        raise NumericRangeException("Too Large Range, numeric equality test unlikely to be accurate!")
    # If the function is the same at all of these points, probably can't conclude anything;
    # Unless the expected result is actually a constant (no free symbols)
    if (numeric_range < 10E-10) and (len(target_expr.free_symbols) > 0):
        raise NumericRangeException("Too Small Range, numeric equality test unlikely to be accurate!")

    # Calculate the difference between the two arrays, if it is less than 10E-8% of
    # the largest value in the target function; the two things are probably equal!
    # This will cope perfectly with complex numbers too!
    diff = numpy.sum(numpy.abs(eval_f_target - eval_f_test))
    print "Numeric Equality Tested: absolute difference of %.6E" % diff
    if diff <= (1E-10 * numpy.max(numpy.abs(eval_f_target))):
        print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = "numeric"
        return True
    else:
        return False


def expr_equality(test_expr, target_expr):
    """Given two sympy expressions: test for exact, symbolic and numeric equality.

       Check two sympy expressions for equality, throwing a TypeError if either
       of the provided sympy objects is not an expression.
        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    if test_expr.is_Relational or target_expr.is_Relational:
        raise TypeError("Can't check nested equalities/inequalities!")
    equality_type = "exact"
    equal = exact_match(test_expr, target_expr)
    if not equal:
        # Now is the best time to simplify any derivatives:
        # FIXME - IF FALSE: we don't want to do this right now!
        if False and target_expr.has(sympy.Derivative) or test_expr.has(sympy.Derivative):
            print "[SIMPLIFY DERIVATIVES]"
            target_expr = simplify_derivatives(target_expr)
            test_expr = simplify_derivatives(test_expr)
        # Then try checking for symbolic equality:
        equality_type = "symbolic"
        equal = symbolic_equality(test_expr, target_expr)
    if not equal:
        equality_type = "numeric"
        equal = numeric_equality(test_expr, target_expr)
    return equal, equality_type


def general_equality(test_expr, target_expr):
    """Given two general sympy objects: test for exact, symbolic and numeric equality.

        - 'test_expr' should be the untrusted sympy object to check.
        - 'target_expr' should be the trusted sympy object to match against.
    """
    equal, equality_type = known_equal_pair(test_expr, target_expr)
    # If this is a known pair: return immediately:
    if equal:
        return equal, equality_type
    # Dealing with an equation?
    if target_expr.is_Equality:
        print "[[EQUATION CHECK]]"
        if not test_expr.is_Equality:
            raise EquationTypeMismatch("Expected an equation!")
        print "[LHS == LHS]"
        equal_lhs, equality_type_lhs = expr_equality(test_expr.lhs, target_expr.lhs)
        print "[RHS == RHS]"
        equal_rhs, equality_type_rhs = expr_equality(test_expr.rhs, target_expr.rhs)
        equal = equal_lhs and equal_rhs
        equality_type = eq_type_order([equality_type_lhs, equality_type_rhs])
        if not equal:
            print "[CROSS SIDE CHECK]"
            print "[LHS == RHS]"
            equal_lhs, equality_type_lhs = expr_equality(test_expr.rhs, target_expr.lhs)
            print "[RHS == LHS]"
            equal_rhs, equality_type_rhs = expr_equality(test_expr.lhs, target_expr.rhs)
            equal = equal_lhs and equal_rhs
            equality_type = eq_type_order([equality_type_lhs, equality_type_rhs])
        return equal, equality_type
    # Dealing with an inequality?
    elif target_expr.is_Relational:
        print "[[INEQUALITY CHECK]]"
        if not test_expr.is_Relational:
            raise EquationTypeMismatch("Expected an inequality!")
        print "[LTS == LTS]"
        equal_lts, equality_type_lts = expr_equality(test_expr.lts, target_expr.lts)
        print "[GTS == GTS]"
        equal_gts, equality_type_gts = expr_equality(test_expr.gts, target_expr.gts)
        # Ensure that if one is strict inequlity, they both are. Or if one isn't, the other isn't.
        equal_rel = not (("Strict" in target_expr.func.__name__) != ("Strict" in test_expr.func.__name__))  # NOT XOR
        print "[INEQUALITY TYPE CHECK]"
        if not equal_rel:
            print "Strict vs Non-Strict Inequality Mismatch!"
        equal = equal_lts and equal_gts and equal_rel
        equality_type = eq_type_order([equality_type_lts, equality_type_gts])
        return equal, equality_type
    # Else assume an expression:
    else:
        print "[[EXPRESSION CHECK]]"
        if test_expr.is_Equality or test_expr.is_Relational:
            raise EquationTypeMismatch("Expected an expression!")
        return expr_equality(test_expr, target_expr)


def plus_minus_checker(test_str, target_str, symbols=None, check_symbols=True):
    """A checking function for inputs containing the ± character.

       Using the same arguments as the check(...) function, deals with multivalued
       input which contains the ± character. This requires calling check() twice,
       once for the +ve case and once for the -ve case. Doing so does allow full code
       reuse, so equations can contain the plus-or-minus notation and still be checked.
       Returns a similar dict to check().
        - 'test_str' should be the untrusted string for sympy to parse.
        - 'target_str' should be the trusted string to parse and match against.
        - 'symbols' should be a comma separated list of symbols not to split.
        - 'check_symbols' indicates whether to verfiy the symbols used in each
          expression are exactly the same or not; setting this to False will
          allow symbols which cancel out to be included (probably don't want this
          in questions).
    """
    print "[[PLUS-OR-MINUS CHECKING]]"
    if not ((u'±' in target_str) and (u'±' in test_str)):
        print "Plus-or-Minus mismatch between test and target! Can't be equal!"
        print "[[OVERALL RESULT]]"
        print "Equality: False"
        print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            equal=str(False).lower(),
            equality_type="symbolic",
            )
    print "[[Multi-Valued: Case Using +ve Value]]"
    plus = check(test_str.replace(u'±', '+'), target_str.replace(u'±', '+'),
                 symbols=symbols, check_symbols=check_symbols, _quiet=True)
    if "error" in plus:
        # The dictionary is mostly correct, but the target and test strings are wrong:
        plus["target"] = target_str
        plus["test"] = test_str
        plus["case"] = "+"
        print "=" * 50
        return plus
    print "[[Multi-Valued: Case Using -ve Value]]"
    minus = check(test_str.replace(u'±', '-'), target_str.replace(u'±', '-'),
                  symbols=symbols, check_symbols=check_symbols, _quiet=True)
    if "error" in minus:
        # The dictionary is mostly correct, but the target and test strings are wrong:
        minus["target"] = target_str
        minus["test"] = test_str
        minus["case"] = "-"
        print "=" * 50
        return minus
    equal = (plus["equal"] == "true" and minus["equal"] == "true")
    equality_type = eq_type_order([plus["equality_type"], minus["equality_type"]])
    print "[[OVERALL RESULT]]"
    print "Equality: %s" % equal
    print "=" * 50
    # We'll return only the strictly positive parsed target and test values for now:
    return dict(
                target=target_str,
                test=test_str,
                parsedTarget=plus["parsedTarget"],
                parsedTest=plus["parsedTest"],
                equal=str(equal).lower(),
                equality_type=equality_type,
            )


def check(test_str, target_str, symbols=None, check_symbols=True, description=None,
          _quiet=False):
    """The main checking function, calls each of the equality checking functions as required.

       Returns a dict describing the equality; with important keys being 'equal',
       and 'equality_type'. The key 'error' is added if something went wrong, and
       this should always be checked for first.

        - 'test_str' should be the untrusted string for sympy to parse.
        - 'target_str' should be the trusted string to parse and match against.
        - 'symbols' should be a comma separated list of symbols not to split.
        - 'check_symbols' indicates whether to verfiy the symbols used in each
          expression are exactly the same or not; setting this to False will
          allow symbols which cancel out to be included (probably don't want this
          in questions).
        - 'description' is an optional description to print before the checker's
          output to stdout which can be used to improve logging.
        - '_quiet' is an internal argument used to suppress some output when
          this function is called from plus_minus_checker().
    """
    # If nothing to parse, fail. On server, this will be caught in check_endpoint()
    if (target_str == "") or (test_str == ""):
        return dict(error="Empty string as argument.")

    # Cleanup the strings before anything is done to them:
    target_str = cleanup_string(target_str)
    test_str = cleanup_string(test_str)

    # Suppress this output:
    if not _quiet:
        print "=" * 50
        # For logging purposes, if we have a description: print it!
        if description is not None:
            print description
            print "=" * 50

    print "Target string: '%s'" % target_str
    print "Test string: '%s'" % test_str

    # If the input contains a plus-or-minus sign, we need to do things differently:
    if ((u'±' in target_str) or (u'±' in test_str)):
        return plus_minus_checker(test_str, target_str, symbols=symbols, check_symbols=check_symbols)

    # These two lines address some security issues - don't use default transformations, and whitelist of functions to match.
    # This can't stop some builtin functions, but hopefully removing "." and "[]" will reduce this problem
    transforms = (sympy.parsing.sympy_parser.auto_number, sympy.parsing.sympy_parser.auto_symbol,
                  sympy.parsing.sympy_parser.convert_xor, sympy_parser.split_symbols, sympy_parser.implicit_multiplication)
    global_dict = {"Symbol": sympy.Symbol, "Integer": sympy.Integer, "Float": sympy.Float, "Rational": sympy.Rational,
                   "Mul": sympy.Mul, "Pow": sympy.Pow, "Add": sympy.Add,
                   "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
                   "arcsin": sympy.asin, "arccos": sympy.acos, "arctan": sympy.atan,
                   "sinh": sympy.sinh, "cosh": sympy.cosh, "tanh": sympy.tanh,
                   "arcsinh": sympy.asinh, "arccosh": sympy.acosh, "arctanh": sympy.atanh,
                   "cosec": sympy.csc, "sec": sympy.sec, "cot": sympy.cot,
                   "arccosec": sympy.acsc, "arcsec": sympy.asec, "arccot": sympy.acot,
                   "cosech": sympy.csch, "sech": sympy.sech, "coth": sympy.coth,
                   "exp": sympy.exp, "log": sympy.log, "ln": sympy.ln,
                   "sqrt": sympy.sqrt, "abs": sympy.Abs, "factorial": factorial,
                   "iI": sympy.I, "piPI": sympy.pi, "eE": sympy.E,
                   "lamda": sympy.abc.lamda, "Rel": sympy.Rel, "Eq": Equal,
                   "Derivative": sympy.Derivative}

    # Prevent splitting of known symbols (symbols with underscores are left alone by default anyway)
    local_dict = {}
    if symbols is not None:
        for s in symbols.split(","):
            local_dict[s] = sympy.Symbol(s)

    print "[[PARSE EXPRESSIONS]]"
    # Parse the trusted target expression:
    target_expr = parse_expression(target_str, transforms=transforms, local_dict=local_dict, global_dict=global_dict)
    # Parse the untrusted test expression:
    test_expr = parse_expression(test_str, transforms=transforms, local_dict=local_dict, global_dict=global_dict)

    if target_expr is None:
        print "ERROR: TRUSTED EXPRESSION CANNOT BE PARSED!"
        if not _quiet:
            print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            error="Parsing TARGET Expression Failed!",
            code=400  # Add a Bad Request status code because this is serious
            )
    if test_expr is None:
        print "Incorrectly formatted ToCheck expression."
        if not _quiet:
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
                print "[[RESULT]]\nEquality: False"
                if not _quiet:
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
        # Then check for equality proper:
        equal, equality_type = general_equality(test_expr, target_expr)
    except EquationTypeMismatch, e:
        print "Equation/Expression Type Mismatch: can't be equal!"
        equal = False
        equality_type = "symbolic"
    except (SyntaxError, TypeError, AttributeError, NumericRangeException), e:
        print "Error when comparing expressions: '%s'." % e
        if not _quiet:
            print "=" * 50
        return dict(
            target=target_str,
            test=test_str,
            parsedTarget=str(target_expr),
            parsedTest=str(test_expr),
            error="Comparison of expressions failed: '%s'" % e,
            )
    print "[[RESULT]]"
    if equal and (equality_type != "exact") and ((target_expr, test_expr) not in KNOWN_PAIRS):
        print "INFO: Adding known pair (%s, %s)" % (target_expr, test_expr)
        KNOWN_PAIRS[(target_expr, test_expr)] = equality_type
    print "Equality: %s" % equal
    if not _quiet:
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
        print "=" * 50
        print "ERROR: Ill-formed request!"
        print body
        print "=" * 50
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    target_str = body["target"]
    test_str = body["test"]

    if "description" in body:
        description = str(body["description"])
    else:
        description = None

    if (target_str == "") or (test_str == ""):
        print "=" * 50
        if description is not None:
            print description
            print "=" * 50
        print "ERROR: Empty string in request!"
        print "Target: '%s'\nTest: '%s'" % (target_str, test_str)
        print "=" * 50
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    if "symbols" in body:
        symbols = str(body["symbols"])
    else:
        symbols = None

    if "check_symbols" in body:
        check_symbols = str(body["check_symbols"]).lower() == "true"
    else:
        check_symbols = True

    # To reduce computation issues on single-threaded server, institute a timeout
    # for requests. If it takes longer than this to process, return an error.
    # This cannot interrupt numpy's computation, so care must be taken in selecting
    # a value for MAX_REQUEST_COMPUTATION_TIME.
    try:
        with TimeoutProtection(MAX_REQUEST_COMPUTATION_TIME):
            response_dict = check(test_str, target_str, symbols, check_symbols, description)
            return jsonify(**response_dict)
    except TimeoutException, e:
        print "ERROR: %s - Request took too long to process, aborting!" % type(e).__name__
        print "=" * 50
        error_dict = dict(
            target=target_str,
            test=test_str,
            error="Request took too long to process!",
            )
        return jsonify(**error_dict)


@app.route('/', methods=["GET"])
def ping():
    return jsonify(code=200)


if __name__ == '__main__':
    # Make sure all outgoing error messages are in JSON format.
    # This will only work provided debug=False - otherwise the debugger hijacks them!
    for code in default_exceptions.iterkeys():
        app.register_error_handler(code, make_json_error)
    # Then run the app
    app.run(port=5000, host="0.0.0.0", debug=False)
