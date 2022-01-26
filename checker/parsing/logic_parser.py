import re
import tokenize
import sympy
from sympy.parsing import sympy_parser

from . import ParsingException, UnsafeInputException
from .utils import process_unicode_chars, auto_symbol, integer_to_bool, rewrite_inline_xor, evaluateFalse

__all__ = ["cleanup_string", "parse_expr"]


# We need to be able to sanitise user input. Whitelist allowed characters:
ALLOWED_CHARACTER_LIST = ["\x20",            # space
                          "\x26",            # ampersand
                          "\x28-\x29",       # left and right brackets
                          # "\x2A",            # plus
                          # "\x2E",            # full stop
                          "\x3C-\x3E",       # less than, equal, greater than
                          "\x30-\x31",       # numbers 0 and 1
                          "\x41-\x5A",       # uppercase letters A-Z
                          "\x5E",            # caret symbol
                          "\x61-\x7A",       # lowercase letters a-z
                          "\x7C",            # vertical line
                          "\x7E"]            # tilde

# Join these into a regular expression that matches everything except allowed characters:
UNSAFE_CHARACTERS_REGEX = r"[^" + "".join(ALLOWED_CHARACTER_LIST) + r"]+"
# Match all non-ASCII characters:
NON_ASCII_CHAR_REGEX = r"[^\x00-\x7F]+"


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
    string = re.sub(r'(?<![=<>])=(?![=<>])', '==', string)  # Replace all single equals signs with double equals
    return string


#####
# Custom Parsers:
#####

# These constants are needed to address some security issues.
# We don't want to use the default transformations, and we need to use a
# whitelist of functions the parser should allow to match.
_TRANSFORMS = (rewrite_inline_xor, integer_to_bool, sympy_parser.auto_number, auto_symbol, sympy_parser.split_symbols)

_GLOBAL_DICT = {
    "Symbol": sympy.Symbol,
    "Eq": sympy.Equivalent, "Implies": sympy.Implies,
    "And": sympy.And, "Or": sympy.Or, "Not": sympy.Not, "Xor": sympy.Xor,
    "and": sympy.And, "or": sympy.Or, "not": sympy.Not, "xor": sympy.Xor,
    "True": sympy.true, "False": sympy.false
}

_PARSE_HINTS = {}


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

    try:
        code = sympy_parser.stringify_expr(expression_str, local_dict, _GLOBAL_DICT, _TRANSFORMS)
        ef_code = evaluateFalse(code)
        code_compiled = compile(ef_code, '<string>', 'eval')
        return sympy_parser.eval_expr(code_compiled, local_dict, _GLOBAL_DICT)
    except (tokenize.TokenError, SyntaxError, TypeError, AttributeError, sympy.SympifyError) as e:
        print(("ERROR: {0} - {1}".format(type(e).__name__, str(e))).strip(":- "))
        raise ParsingException
