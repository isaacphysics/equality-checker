import sympy

from .utils import known_equal_pair, contains_incorrect_symbols
from .utils import EqualityType
from .parsing import logic_parser, UnsafeInputException


__all__ = ["check"]


KNOWN_PAIRS = dict()


def parse_expression(expression_str, *, local_dict=None):
    """Take a string containing a mathematical expression and return a sympy expression.

       Wrap the parsing class function parse_expr(...) and catch any exceptions
       that occur.
        - 'local_dict' can be a dictionary of (name, sympy.Symbol(...)) pairs, where
          the string 'name' will not be split up and will be turned into the symbol
          specified. It may be None.
    """
    try:
        return logic_parser.parse_expr(expression_str, local_dict=local_dict)
    except logic_parser.ParsingException:
        print("Incorrectly formatted expression.")
        print("Fail: '{}'.".format(expression_str))
        return None


def exact_match(test_expr, target_expr):
    """Test if the entered expression exactly matches the known expression.

       This performs as little simplification of the boolean expression as
       possible, allowing only the commutativity or AND and OR.

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

       Use the sympy 'simplify_logic' function to simplify the two boolean
       expressions as much as possible. Two equilvalent expressions MUST simplify
       to the same thing, and then they can be tested for equivalence again.

       Returns True if sympy can determine that the two expressions are equal,
       and returns False if they are not equal.

        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    print("[SYMBOLIC TEST]")
    try:
        simplified_target = sympy.simplify_logic(target_expr)
        simplified_test = sympy.simplify_logic(test_expr)
        if simplified_target == simplified_test or sympy.srepr(simplified_target) == sympy.srepr(simplified_test):
            print("Symbolic match.")
            print("INFO: Adding known pair ({0}, {1})".format(target_expr, test_expr))
            KNOWN_PAIRS[(target_expr, test_expr)] = EqualityType.SYMBOLIC
            return True
        else:
            return False
    except NotImplementedError as e:
        print("{0}: {1} - Can't check symbolic equality!".format(type(e).__name__, str(e).capitalize()))
        return False


def expr_equality(test_expr, target_expr):
    """Given two sympy expressions: test for exact, symbolic and numeric equality.

       Check two sympy expressions for equality, throwing a TypeError if either
       of the provided sympy objects is not an expression.
        - 'test_expr' should be the untrusted sympy expression to check.
        - 'target_expr' should be the trusted sympy expression to match against.
    """
    equality_type = EqualityType.EXACT
    equal = exact_match(test_expr, target_expr)
    if not equal:
        # Then try checking for symbolic equality:
        equality_type = EqualityType.SYMBOLIC
        equal = symbolic_equality(test_expr, target_expr)
    return equal, equality_type


def general_equality(test_expr, target_expr):
    """Given two general sympy objects: test for exact, symbolic and numeric equality.

        - 'test_expr' should be the untrusted sympy object to check.
        - 'target_expr' should be the trusted sympy object to match against.
    """
    equal, equality_type = known_equal_pair(KNOWN_PAIRS, test_expr, target_expr)
    # If this is a known pair: return immediately:
    if equal:
        return equal, equality_type
    else:
        print("[[EXPRESSION CHECK]]")
        return expr_equality(test_expr, target_expr)


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
        print("[LOGIC]")

    # If nothing to parse, fail. On server, this will be caught in check_endpoint()
    if (target_str == "") or (test_str == ""):
        print("ERROR: No input provided!")
        if not _quiet:
            print("=" * 50)
        return dict(error="Empty string as argument.")

    # Cleanup the strings before anything is done to them:
    error_is_test = False
    try:
        target_str = logic_parser.cleanup_string(target_str, reject_unsafe_input=True)
        error_is_test = True
        test_str = logic_parser.cleanup_string(test_str, reject_unsafe_input=True)
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

    print("[[PARSE EXPRESSIONS]]")
    # Parse the trusted target expression:
    target_expr = parse_expression(target_str)
    # Parse the untrusted test expression:
    test_expr = parse_expression(test_str)

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
                result["equality_type"] = EqualityType.SYMBOLIC.value
                result["incorrect_symbols"] = incorrect_symbols
                return result
        # Then check for equality proper:
        equal, equality_type = general_equality(test_expr, target_expr)
    except (SyntaxError, TypeError, AttributeError) as e:
        print("Error when comparing expressions: '{}'.".format(e))
        if not _quiet:
            print("=" * 50)
        result["error"] = "Comparison of expressions failed: '{}'".format(e)
        return result

    print("[[RESULT]]")
    if equal and (equality_type is not EqualityType.EXACT) and ((target_expr, test_expr) not in KNOWN_PAIRS):
        print("INFO: Adding known pair ({0}, {1})".format(target_expr, test_expr))
        KNOWN_PAIRS[(target_expr, test_expr)] = equality_type
    print("Equality: {}".format(equal))
    if not _quiet:
        print("=" * 50)
    result["equal"] = str(equal).lower()
    result["equality_type"] = equality_type.value
    return result
