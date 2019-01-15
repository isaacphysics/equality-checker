# -*- coding: utf-8 -*-

import numpy
import sympy

from .parsing import maths_parser


# Hack to fix a bug with lambdify and complex infinity ('zoo') when transforming
# to NumPy for evaluation. Map complex infinity to Not a Number ('nan').
from sympy.utilities.lambdify import NUMPY_TRANSLATIONS
NUMPY_TRANSLATIONS["zoo"] = "nan"


__all__ = ["check"]


KNOWN_PAIRS = dict()

# Numpy (understandably) doesn't have all 24 trig functions defined. Define those missing for completeness. (No hyperbolic inverses for now!)
NUMPY_MISSING_FN = {"csc": lambda x: 1/numpy.sin(x), "sec": lambda x: 1/numpy.cos(x), "cot": lambda x: 1/numpy.tan(x),
                    "acsc": lambda x: numpy.arcsin(numpy.float_power(x, -1)), "asec": lambda x: numpy.arccos(numpy.float_power(x, -1)), "acot": lambda x: numpy.arctan(numpy.float_power(x, -1)),
                    "asinh": lambda x: numpy.arcsinh(x), "acosh": lambda x: numpy.arccosh(x), "atanh": lambda x: numpy.arctanh(x),
                    "csch": lambda x: 1/numpy.sinh(x), "sech": lambda x: 1/numpy.cosh(x), "coth": lambda x: 1/numpy.tanh(x)}
# Make a complex form of the above for no-variable cases of numeric evaluation.
# (Late Binding means that can't just use NUMPY_MISSING_FN[k] since this isn't evaluated in
# the for loop properly. But adding it as a default argument to the lambda *does* cause the
# evaluation and so the two effects cancel out. Neat!)
NUMPY_COMPLEX_FN = {k: lambda x, f=NUMPY_MISSING_FN[k]: f(x + 0j) for k in list(NUMPY_MISSING_FN.keys())}

# Whether to allow derivative simplification.
# FIXME: this should be a parameter of the check(...) method.
SIMPLIFY_DERIVATIVES = False


class NumericRangeException(Exception):
    """An exception to be raised when numeric values are rejected."""
    pass


class EquationTypeMismatch(TypeError):
    """An exception to be raised when equations are compared to expressions."""
    pass


def known_equal_pair(test_expr, target_expr):
    """In lieu of any real persistent cache of known pairs, just use a dict for now!

       Checks if the two expressions are known pairs from previous testing; this
       should reduce calls to 'simplify' and the numeric testing, both of which
       are computationally costly and slow.
    """
    print("[[KNOWN PAIR CHECK]]")
    pair = (target_expr, test_expr)
    if pair in KNOWN_PAIRS:
        print("Known Pair from {} equality!".format(KNOWN_PAIRS[pair]))
        return (True, KNOWN_PAIRS[pair])
    else:
        return (False, "known")


def parse_expression(expression_str, *, local_dict=None):
    """Take a string containing a mathematical expression and return a sympy expression.

       Wrap the parsing class function parse_expr(...) and catch any exceptions
       that occur.
        - 'local_dict' can be a dictionary of (name, sympy.Symbol(...)) pairs, where
          the string 'name' will not be split up and will be turned into the symbol
          specified. It may be None.
    """
    try:
        return maths_parser.parse_expr(expression_str, local_dict=local_dict)
    except maths_parser.ParsingException:
        print("Incorrectly formatted expression.")
        print("Fail: '{}'.".format(expression_str))
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
    print("[[SYMBOL CHECK]]")
    if test_expr.free_symbols != target_expr.free_symbols:
        print("Symbol mismatch between test and target!")
        result = dict()
        missing = ",".join(map(str, list(target_expr.free_symbols.difference(test_expr.free_symbols))))
        extra = ",".join(map(str, list(test_expr.free_symbols.difference(target_expr.free_symbols))))
        missing = missing.replace("lamda", "lambda").replace("Lamda", "Lambda")
        extra = extra.replace("lamda", "lambda").replace("Lamda", "Lambda")
        if len(missing) > 0:
            print("Test Expression missing: {}".format(missing))
            result["missing"] = missing
        if len(extra) > 0:
            print("Test Expression has extra: {}".format(extra))
            result["extra"] = extra
        print("Not Equal: Enforcing strict symbol match for correctness!")
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
        raise TypeError("Unexpected list of equality types: {}".format(eq_types))


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
        print("Simplified '{0}' to '{1}'!".format(derivative, d))
    return d


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


def exact_match(test_expr, target_expr):
    """Test if the entered expression exactly matches the known expression.

       This equality checking does not expand brackets or perform much simplification,
       so is useful for checking if the submitted answer requires simplifying.
       Testing is first done using '==' which checks that the order of symbols
       matches and will not recognise 'x + 1' as equal to '1 + x' since we use
       'evaluate=False' everywhere which prevents sorting of arguments.
       The 'srepr' method outputs sympy's internal representation in a canonical sorted
       form and thus, while performing no simplification, it allows ordering to be ignored
       in exact match checking. These two forms are treated equivalently as 'exact'
       matching.

       Returns True if the sympy expressions have the same internal structure,
       and False if not.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    print("[EXACT TEST]")
    if test_expr == target_expr:
        print("Exact Match (with '==')")
        return True
    elif sympy.srepr(test_expr) == sympy.srepr(target_expr):
        # This is a (perfectly acceptable) hack for ordering the atoms of each
        # term, but a more explicit method may be preferable in the future.
        print("Exact Match (with 'srepr')")
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
    print("[SYMBOLIC TEST]")
    # Here we make the assumption that all variables are real and positive to
    # aid the simplification process. Since we do this for numeric checking anyway,
    # it doesn't seem like much of an issue. Removing 'sympy.posify()' below will
    # stop this.
    try:
        if sympy.simplify(sympy.posify(test_expr - target_expr)[0]) == 0:
            print("Symbolic match.")
            print("INFO: Adding known pair ({0}, {1})".format(target_expr, test_expr))
            KNOWN_PAIRS[(target_expr, test_expr)] = "symbolic"
            return True
        else:
            return False
    except NotImplementedError as e:
        print("{0}: {1} - Can't check symbolic equality!".format(type(e).__name__, e.message.capitalize()))
        return False


def numeric_equality(test_expr, target_expr, *, complexify=False):
    """Test if two expressions are numerically equivalent to one another.

       The implementation of this method is liable to change and currently has
       several major flaws. It will sample the test and target functions over
       the free parameters of the target expression. If the test expression has
       more symbols, the parameter space is extended to include these (to test for
       cases where these parameters make no difference). Testing is performed on
       the interval [0, 1) and if 'complexify' is set then complex values are
       allowed, but the samples are still in the interval [0, 1) on the real line.

       Returns True if the two expressions are equal for the sampled points, and
       False otherwise.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
        - 'complexify' is a boolean flag for sampling in the complex plane rather
          than just over the reals.
    """
    print("[NUMERIC TEST]" if not complexify else "[NUMERIC TEST (COMPLEX)]")
    SAMPLE_POINTS = 25
    lambdify_modules = [NUMPY_MISSING_FN, "numpy"]

    # Leave original expressions unchanged, and expand logarithms!
    # NumPy has a log(x) function that takes only one argument, whereas SymPy
    # has a log(x, base) function which would break when calling lambdify if it
    # was left unexpanded.
    target_expr_n = sympy.expand_log(target_expr)
    test_expr_n = sympy.expand_log(test_expr)

    # Replace any derivatives that exist with new dummy symbols, and treat them
    # as independent from the variables they involve. To avoid naming clashes,
    # just name them in ascending numeric order by length of arguments.
    # This ordering helps ensure something like d^2y/dx^2 gets substituted before
    # the implicit inner dy/dx gets replaced and breaks things.
    derivatives = target_expr.atoms(sympy.Derivative).union(test_expr.atoms(sympy.Derivative))
    for d, derivative in enumerate(sorted(derivatives, key=lambda d: len(d.args), reverse=True)):
        derivative_symbol = sympy.Symbol("Derivative_{}".format(d))
        print("Swapping '{0}' into variable '{1}' for numeric evaluation!".format(derivative, derivative_symbol))
        target_expr_n = target_expr_n.subs(derivative, derivative_symbol)
        test_expr_n = test_expr_n.subs(derivative, derivative_symbol)

    # If target has variables not in test, then test cannot possibly be equal.
    # This introduces an asymmetry; target is trusted to only contain necessary symbols,
    # but test is not.
    if len(target_expr_n.free_symbols.difference(test_expr_n.free_symbols)) > 0:
        print("Test expression doesn't contain all target expression variables! Can't be numerically tested.")
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

    try:
        # Make the target expression into something numpy can evaluate, then evaluate
        # for the sample points. This *should* now be safe, but still could be dangerous.
        f_target = sympy.lambdify(shared_variables, target_expr_n, lambdify_modules)
        eval_f_target = f_target(*domain_target)

        # Repeat for the test expression, to get an array of containing SAMPLE_POINTS
        # values of test_expr_n to be compared to target_expr_n
        f_test = sympy.lambdify(test_variables, test_expr_n, lambdify_modules)
        eval_f_test = f_test(*domain_test)
    except OverflowError as e:
        raise NumericRangeException(e.message)

    # Output the function values at the sample points for debugging?
    # The actual domain arrays are probably too long to be worth ever printing.
    print("Target function value(s):")
    print(eval_f_target)
    print("Test function value(s):")
    print(eval_f_test)

    # Can we safely cast the values to 64 bit floats (2 x 64 bits for complex values)?
    # Real values that can be safely cast to 'float64' can always be cast to 'complex128'
    # safely as well, and since eval_f_test may be complex, this errs on the side of caution.
    safe_datatype = "complex128"
    if not all([numpy.can_cast(a, safe_datatype, casting='safe') for a in [eval_f_target, eval_f_test]]):
        raise NumericRangeException("A function has values not representable by 64 bit floats!")

    # If get any NaN's from the functions; things are looking bad:
    if numpy.any(numpy.isnan(eval_f_target)) or numpy.any(numpy.isnan(eval_f_test)):
        # If have not tried using complex numbers, try using those:
        if not complexify:
            print("A function appears to be undefined in the interval [0,1). Trying again with complex values!")
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
    print("Numeric Equality Tested: absolute difference of {:.6E}".format(diff))
    if diff <= (1E-10 * numpy.max(numpy.abs(eval_f_target))):
        print("INFO: Adding known pair ({0}, {1})".format(target_expr, test_expr))
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
        if SIMPLIFY_DERIVATIVES and (target_expr.has(sympy.Derivative) or test_expr.has(sympy.Derivative)):
            print("[SIMPLIFY DERIVATIVES]")
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
        print("[[EQUATION CHECK]]")
        if not test_expr.is_Equality:
            raise EquationTypeMismatch("Expected an equation!")
        print("[LHS == LHS]")
        equal_lhs, equality_type_lhs = expr_equality(test_expr.lhs, target_expr.lhs)
        print("[RHS == RHS]")
        equal_rhs, equality_type_rhs = expr_equality(test_expr.rhs, target_expr.rhs)
        equal = equal_lhs and equal_rhs
        equality_type = eq_type_order([equality_type_lhs, equality_type_rhs])
        if not equal:
            print("[CROSS SIDE CHECK]")
            print("[LHS == RHS]")
            equal_lhs, equality_type_lhs = expr_equality(test_expr.rhs, target_expr.lhs)
            print("[RHS == LHS]")
            equal_rhs, equality_type_rhs = expr_equality(test_expr.lhs, target_expr.rhs)
            equal = equal_lhs and equal_rhs
            equality_type = eq_type_order([equality_type_lhs, equality_type_rhs])
        return equal, equality_type
    # Dealing with an inequality?
    elif target_expr.is_Relational:
        print("[[INEQUALITY CHECK]]")
        if not test_expr.is_Relational:
            raise EquationTypeMismatch("Expected an inequality!")
        print("[LTS == LTS]")
        equal_lts, equality_type_lts = expr_equality(test_expr.lts, target_expr.lts)
        print("[GTS == GTS]")
        equal_gts, equality_type_gts = expr_equality(test_expr.gts, target_expr.gts)
        # Ensure that if one is strict inequlity, they both are. Or if one isn't, the other isn't.
        equal_rel = not (("Strict" in target_expr.func.__name__) != ("Strict" in test_expr.func.__name__))  # NOT XOR
        print("[INEQUALITY TYPE CHECK]")
        if not equal_rel:
            print("Strict vs Non-Strict Inequality Mismatch!")
        equal = equal_lts and equal_gts and equal_rel
        equality_type = eq_type_order([equality_type_lts, equality_type_gts])
        return equal, equality_type
    # Else assume an expression:
    else:
        print("[[EXPRESSION CHECK]]")
        if test_expr.is_Equality or test_expr.is_Relational:
            raise EquationTypeMismatch("Expected an expression!")
        return expr_equality(test_expr, target_expr)


def plus_minus_checker(test_str, target_str, *, symbols=None, check_symbols=True):
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
    print("[[PLUS-OR-MINUS CHECKING]]")
    if not (('±' in target_str) and ('±' in test_str)):
        print("Plus-or-Minus mismatch between test and target! Can't be equal!")
        print("[[OVERALL RESULT]]")
        print("Equality: False")
        print("=" * 50)
        return dict(
            target=target_str,
            test=test_str,
            equal=str(False).lower(),
            equality_type="symbolic",
            )
    print("[[Multi-Valued: Case Using +ve Value]]")
    plus = check(test_str.replace('±', '+'), target_str.replace('±', '+'),
                 symbols=symbols, check_symbols=check_symbols, _quiet=True)
    if "error" in plus:
        # The dictionary is mostly correct, but the target and test strings are wrong:
        plus["target"] = target_str
        plus["test"] = test_str
        plus["case"] = "+"
        print("=" * 50)
        return plus
    print("[[Multi-Valued: Case Using -ve Value]]")
    minus = check(test_str.replace('±', '-'), target_str.replace('±', '-'),
                  symbols=symbols, check_symbols=check_symbols, _quiet=True)
    if "error" in minus:
        # The dictionary is mostly correct, but the target and test strings are wrong:
        minus["target"] = target_str
        minus["test"] = test_str
        minus["case"] = "-"
        print("=" * 50)
        return minus
    equal = (plus["equal"] == "true" and minus["equal"] == "true")
    equality_type = eq_type_order([plus["equality_type"], minus["equality_type"]])
    print("[[OVERALL RESULT]]")
    print("Equality: {}".format(equal))
    print("=" * 50)
    # We'll return only the strictly positive parsed target and test values for now:
    return dict(
                target=target_str,
                test=test_str,
                parsed_target=plus["parsed_target"],
                parsed_test=plus["parsed_test"],
                equal=str(equal).lower(),
                equality_type=equality_type,
            )


def check(test_str, target_str, *, symbols=None, check_symbols=True, description=None,
          _quiet=False):
    """The main checking function, calls each of the equality checking functions as required.

       Returns a dict describing the equality; with important keys being 'equal',
       and 'equality_type'. The key 'error' is added if something went wrong, and
       this should always be checked for first.

        - 'test_str' should be the untrusted string for sympy to parse.
        - 'target_str' should be the trusted string to parse and match against.
        - 'symbols' should be a string list or comma separated string of symbols
           not to split during parsing.
        - 'check_symbols' indicates whether to verfiy the symbols used in each
          expression are exactly the same or not; setting this to False will
          allow symbols which cancel out to be included (probably don't want this
          in questions).
        - 'description' is an optional description to print before the checker's
          output to stdout which can be used to improve logging.
        - '_quiet' is an internal argument used to suppress some output when
          this function is called from plus_minus_checker().
    """

    # Suppress this output if necessary:
    if not _quiet:
        print("=" * 50)
        # For logging purposes, if we have a description: print it!
        if description is not None:
            print(description)
            print("=" * 50)

    # If nothing to parse, fail. On server, this will be caught in check_endpoint()
    if (target_str == "") or (test_str == ""):
        print("ERROR: No input provided!")
        if not _quiet:
            print("=" * 50)
        return dict(error="Empty string as argument.")

    # Cleanup the strings before anything is done to them:
    error_is_test = False
    try:
        target_str = maths_parser.cleanup_string(target_str, reject_unsafe_input=True)
        error_is_test = True
        test_str = maths_parser.cleanup_string(test_str, reject_unsafe_input=True)
    except UnsafeInputException:
        print("ERROR: Input contained non-whitelisted characters!")
        result = dict(error="Bad input provided!")
        if error_is_test:
            print("Test string: '{}'".format(test_str))
            result["syntax_error"] = str(True).lower()
        if not _quiet:
            print("=" * 50)
        return result

    print("Target string: '{}'".format(target_str))
    print("Test string: '{}'".format(test_str))

    # If the input contains a plus-or-minus sign, we need to do things differently:
    if (('±' in target_str) or ('±' in test_str)):
        return plus_minus_checker(test_str, target_str, symbols=symbols, check_symbols=check_symbols)

    # Prevent splitting of known symbols (symbols with underscores are left alone by default anyway):
    local_dict = {}
    if symbols is not None:
        if isinstance(symbols, str) or isinstance(symbols, str):
            symbols = symbols.split(",")
        for s in symbols:
            s = s.strip()
            if maths_parser.is_valid_symbol(s):
                # Only want symbols here, not functions or operators!
                local_dict[s] = sympy.Symbol(s)

    print("[[PARSE EXPRESSIONS]]")
    # Parse the trusted target expression:
    target_expr = parse_expression(target_str, local_dict=local_dict)
    # Parse the untrusted test expression:
    test_expr = parse_expression(test_str, local_dict=local_dict)

    result = dict(target=target_str, test=test_str)

    if target_expr is None:
        print("ERROR: TRUSTED EXPRESSION CANNOT BE PARSED!")
        if not _quiet:
            print("=" * 50)
        result["error"] = "Parsing TARGET Expression Failed!"
        result["code"] = 400  # This is fatal!
        return result
    if test_expr is None:
        print("Incorrectly formatted ToCheck expression.")
        if not _quiet:
            print("=" * 50)
        result["error"] = "Parsing Test Expression Failed!"
        result["syntax_error"] = str(True).lower()
        return result

    result["parsed_target"] = str(target_expr)
    result["parsed_test"] = str(test_expr)

    # Now check for symbol match and equality:
    try:
        print("Parsed Target: {0}\nParsed ToCheck: {1}".format(target_expr, test_expr))
        if check_symbols:  # Do we have same set of symbols in each?
            incorrect_symbols = contains_incorrect_symbols(test_expr, target_expr)
            if incorrect_symbols is not None:
                print("[[RESULT]]\nEquality: False")
                if not _quiet:
                    print("=" * 50)

                result["equal"] = str(False).lower()
                result["equality_type"] = "symbolic"
                result["incorrect_symbols"] = incorrect_symbols
                return result
        # Then check for equality proper:
        equal, equality_type = general_equality(test_expr, target_expr)
    except EquationTypeMismatch:
        print("Equation/Expression Type Mismatch: can't be equal!")
        equal = False
        equality_type = "symbolic"
    except (SyntaxError, TypeError, AttributeError, NumericRangeException) as e:
        print("Error when comparing expressions: '{}'.".format(e))
        if not _quiet:
            print("=" * 50)
        result["error"] = "Comparison of expressions failed: '{}'".format(e)
        return result

    print("[[RESULT]]")
    if equal and (equality_type != "exact") and ((target_expr, test_expr) not in KNOWN_PAIRS):
        print("INFO: Adding known pair ({0}, {1})".format(target_expr, test_expr))
        KNOWN_PAIRS[(target_expr, test_expr)] = equality_type
    print("Equality: {}".format(equal))
    if not _quiet:
        print("=" * 50)
    result["equal"] = str(equal).lower()
    result["equality_type"] = equality_type
    return result
