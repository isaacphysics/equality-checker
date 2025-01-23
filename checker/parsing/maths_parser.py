import re
import tokenize
import sympy
import sympy.abc
from sympy.parsing import sympy_parser
from sympy.core.numbers import Integer, Float, Rational

from . import ParsingException, UnsafeInputException
from .utils import process_unicode_chars, auto_symbol, evaluateFalse

__all__ = ["cleanup_string", "is_valid_symbol", "parse_expr"]


# We need to be able to sanitise user input. Whitelist allowed characters:
ALLOWED_CHARACTER_LIST = ["\x20",            # space
                          "\x28-\x29",       # left and right brackets
                          "\x2A-\x2F",       # times, plus, comma, minus, decimal point, divide
                          "\x30-\x39",       # numbers 0-9
                          "\x3C-\x3E",       # less than, equal, greater than
                          "\x41-\x5A",       # uppercase letters A-Z
                          "\x5E-\x5F",       # caret symbol, underscore
                          "\x61-\x7A",       # lowercase letters a-z
                          "\u00B1"]          # plus or minus symbol

# Join these into a regular expression that matches everything except allowed characters:
UNSAFE_CHARACTERS_REGEX = r"[^" + "".join(ALLOWED_CHARACTER_LIST) + r"]+"
# Match all non-ASCII characters:
NON_ASCII_CHAR_REGEX = r"[^\x00-\x7F]+"
# Symbols may only contain 0-9, A-Z, a-z and underscores:
NON_SYMBOL_REGEX = r"[^\x30-\x39\x41-\x5A\x61-\x7A\x5F]+"


#####
# Parsing Cleanup
#####

def cleanup_string(string, *, reject_unsafe_input):
    """Some simple sanity checking and cleanup to perform on passed in strings.

       Since arbitrary strings are passed in, and 'eval' is used implicitly by
       sympy; try and remove the worst offending things from strings.
    """
    # Flask gives us unicode objects anyway, the command line might not!
    if not isinstance(string, str):
        string = str(string.decode('utf-8'))  # We'll hope it's UTF-8
    # Swap any known safe Unicode characters with their ASCII equivalents:
    string = re.sub(NON_ASCII_CHAR_REGEX, process_unicode_chars, string)
    # Replace all non-whitelisted characters in the input:
    string = re.sub(UNSAFE_CHARACTERS_REGEX, '?', string)
    if reject_unsafe_input:
        # If we have non-whitelisted characters, raise an exception:
        if "?" in string:
            # We replaced all non-whitelisted characters with '?' (and '?' is not whitelisted)
            # so if any '?' characters exist the string must have contained bad input.
            raise UnsafeInputException("Unexpected input characters provided!")
    else:
        # otherwise just swap the blacklisted characters for spaces and proceed.
        string = string.replace("?", " ")
    # Further cleanup, because some allowed characters are only allowed in certain circumstances:
    string = re.sub(r'([^0-9])\.([^0-9])', r'\g<1> \g<2>', string)  # Don't allow the . character between non-numbers
    string = re.sub(r'(.?)\.([^0-9])', r'\g<1> \g<2>', string)  # Don't allow the . character before a non-numeric character,
    #                                                            but have to allow it after for cases like (.5) which are valid.
    string = string.replace("lambda", "lamda").replace("Lambda", "Lamda")  # We can't override the built-in keyword
    string = string.replace("__", " ")  # We don't need double underscores, exploits do
    string = re.sub(r'(?<![=<>])=(?![=<>])', '==', string)  # Replace all single equals signs with double equals
    return string


def is_valid_symbol(string):
    """Test whether a string can be a valid symbol.

       Useful for filtering out functions and operators, and for blacklisting
       metasymbols starting with an underscore.
    """
    if len(string) == 0:
        return False
    if re.search(NON_SYMBOL_REGEX, string) is not None:
        return False
    if string.startswith("_"):
        return False
    return True


#####
# Custom Symbol / Function / Operator Classes:
#####

class Equal(sympy.Equality):
    """A custom class to override sympy.Equality's str method."""
    def __str__(self):
        """Print the equation in a nice way!"""
        return "{0} == {1}".format(self.lhs, self.rhs)

    def __repr__(self):
        """Print the equation in a nice way!"""
        return str(self)


def logarithm(argument, base=10, **kwargs):
    """Enforce that the default base of logarithms is the more intuitive base 10.

       SymPy does what many maths packages do, and defaults to the natural
       logarithm for 'log'.
    """
    return sympy.log(argument, base, **kwargs)


def factorial(n):
    """Stop sympy blindly calculating factorials no matter how large.

       If 'n' is a number of some description, ensure that it is smaller than
       a cutoff, otherwise sympy will simply evaluate it, no matter how long that
       may take to complete!
       - 'n' should be a sympy object, that sympy.factorial(...) can use.
    """
    if isinstance(n, (Integer, Float, Rational)) and n > 50:
        raise ValueError("[Factorial]: Too large integer to compute factorial effectively!")
    else:
        return sympy.factorial(n)


#####
# Custom Parsers:
#####

# These constants are needed to address some security issues.
# We don't want to use the default transformations, and we need to use a
# whitelist of functions the parser should allow to match.
_TRANSFORMS = (
    sympy_parser.auto_number, auto_symbol,
    sympy_parser.convert_xor, sympy_parser.split_symbols,
    sympy_parser.implicit_multiplication, sympy_parser.function_exponentiation
)

_GLOBAL_DICT = {
    # Classes of variable:
    "Symbol": sympy.Symbol, "Integer": sympy.Integer,
    "Float": sympy.Float, "Rational": sympy.Rational,
    # Operations:
    "Mul": sympy.Mul, "Pow": sympy.Pow, "Add": sympy.Add,
    "Rel": sympy.Rel, "Eq": Equal,
    # Derivatives:
    "Derivative": sympy.Derivative, "diff": sympy.Derivative,
    # Plain trig:
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "cosec": sympy.csc, "sec": sympy.sec, "cot": sympy.cot,
    "Sin": sympy.sin, "Cos": sympy.cos, "Tan": sympy.tan,
    "Csc": sympy.csc, "Sec": sympy.sec, "Cot": sympy.cot,
    # Inverse trig:
    "arcsin": sympy.asin, "arccos": sympy.acos, "arctan": sympy.atan,
    "arccosec": sympy.acsc, "arcsec": sympy.asec, "arccot": sympy.acot,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "acsc": sympy.acsc, "asec": sympy.asec, "acot": sympy.acot,
    "ArcSin": sympy.asin, "ArcCos": sympy.acos, "ArcTan": sympy.atan,
    "ArcCsc": sympy.acsc, "ArcSec": sympy.asec, "ArcCot": sympy.acot,
    # Hyperbolic trig:
    "sinh": sympy.sinh, "cosh": sympy.cosh, "tanh": sympy.tanh,
    "cosech": sympy.csch, "sech": sympy.sech, "coth": sympy.coth,
    # Inverse hyperbolic trig:
    "arcsinh": sympy.asinh, "arccosh": sympy.acosh, "arctanh": sympy.atanh,
    "arccosech": sympy.acsch, "arcsech": sympy.asech, "arccoth": sympy.acoth,
    "arsinh": sympy.asinh, "arcosh": sympy.acosh, "artanh": sympy.atanh,
    "arcsch": sympy.acsch, "arsech": sympy.asech, "arcoth": sympy.acoth,
    "asinh": sympy.asinh, "acosh": sympy.acosh, "atanh": sympy.atanh,
    "acsch": sympy.acsch, "asech": sympy.asech, "acoth": sympy.acoth,
    # Exponentials and logarithms:
    "exp": sympy.exp, "log": logarithm, "ln": sympy.ln,
    "Exp": sympy.exp, "Log": logarithm, "Ln": sympy.ln,
    # Odds:
    "factorial": factorial,  "Factorial": factorial,
    "sqrt": sympy.sqrt, "abs": sympy.Abs,
    "Sqrt": sympy.sqrt, "Abs": sympy.Abs,
    # We need these to be set, but do not want to override them for maths:
    "true": True, "false": False
}

_PARSE_HINTS = {
    "constant_pi": {"pi": sympy.pi},
    "constant_e": {"e": sympy.E},
    "imaginary_i": {"i": sympy.I},
    "imaginary_j": {"j": sympy.I},
    "natural_logarithm": {"log": sympy.log, "Log": sympy.log}
}


def parse_expr(expression_str, *, local_dict=None, hints=None):
    """A copy of sympy.sympy_parser.parse_expr(...) which prevents all evaluation.

       Arbitrary untrusted input should be cleaned using "cleanup_string" before
       calling this method.
       This is almost a direct copy of the SymPy code, but it also converts inline
       relations like "==" or ">=" to the Relation class to prevent evaluation
       and uses a more aggresive set of transformations and better prevents any
       evaluation. It also ignores the 'global_dict', 'transformations' and
       'evaluate' arguments of the original function.
       Hints can be provided to choose between ambiguous parsings, like 'i' being
       either a letter or sqrt(-1). These should be values from _PARSE_HINTS.
    """
    if not isinstance(expression_str, str):
        return None
    elif expression_str == "" or len(expression_str) == 0:
        return None

    # Ensure the local dictionary is valid:
    if local_dict is None or not isinstance(local_dict, dict):
        local_dict = {}

    # If there are parse hints, add them to the local dictionary:
    if hints is not None and isinstance(hints, (list, tuple)):
        for hint in hints:
            if hint in _PARSE_HINTS:
                local_dict.update(_PARSE_HINTS[hint])

    # FIXME: Avoid parsing issues with notation for Python longs.
    # E.g. the string '2L' should not be interpreted as "two stored as a long".
    # For now, just add a space to force desired behaviour:
    expression_str = re.sub(r'([0-9])([lL])', r'\g<1> \g<2>', expression_str)

    try:
        code = sympy_parser.stringify_expr(expression_str, local_dict, _GLOBAL_DICT, _TRANSFORMS)
        ef_code = evaluateFalse(code)
        code_compiled = compile(ef_code, '<string>', 'eval')
        return sympy_parser.eval_expr(code_compiled, local_dict, _GLOBAL_DICT)
    except (tokenize.TokenError, SyntaxError, TypeError, AttributeError, sympy.SympifyError) as e:
        print(("ERROR: {0} - {1}".format(type(e).__name__, str(e))).strip(":- "))
        raise ParsingException
