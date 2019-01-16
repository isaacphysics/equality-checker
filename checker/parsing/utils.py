import ast
import tokenize
import unicodedata

from sympy.parsing import sympy_parser
from sympy.core.basic import Basic


#####
# Process Unicode characters into equivalent allowed characters:
#####

# Unicode number and fraction name information:
_NUMBERS = {"ZERO": 0, "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6, "SEVEN": 7, "EIGHT": 8, "NINE": 9}
_FRACTIONS = {"HALF": 2, "THIRD": 3, "QUARTER": 4, "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8, "NINTH": 9, "TENTH": 10}
_FRACTIONS.update({"{}S".format(key): value for key, value in _FRACTIONS.items() if key != "HALF"})


def process_unicode_chars(match_object):
    """Clean a string of Unicode characters into allowed characters if possible."""
    result = ""
    prev_name = None
    for char in match_object.group(0):
        name = unicodedata.name(char, None)

        if name is None:
            result += char
        elif name.startswith("SUPERSCRIPT") and name.split()[1] in _NUMBERS:
            number = name.split()[1]
            # Check if this is a continuation of a exponent, or a new one.
            if prev_name is not None and prev_name.startswith("SUPERSCRIPT"):
                result += "{0:d}".format(_NUMBERS[number])
            else:
                result += "**{0:d}".format(_NUMBERS[number])
        elif name.startswith("SUBSCRIPT") and name.split()[1] in _NUMBERS:
            number = name.split()[1]
            # Check if this is a continuation of a subscript, or a new one.
            if prev_name is not None and prev_name.startswith("SUBSCRIPT"):
                result += "{0:d}".format(_NUMBERS[number])
            else:
                result += "_{0:d}".format(_NUMBERS[number])
        elif name.startswith("VULGAR FRACTION"):
            numerator_name = name.split()[2]
            denominator_name = name.split()[3]
            if numerator_name in _NUMBERS and denominator_name in _FRACTIONS:
                result += "({0:d}/{1:d})".format(_NUMBERS[numerator_name], _FRACTIONS[denominator_name])
            else:
                result += char
        elif name in ["MULTIPLICATION SIGN", "ASTERISK OPERATOR"]:
            result += "*"
        elif name in ["DIVISION SIGN", "DIVISION SLASH"]:
            result += "/"
        elif name in ["LESS-THAN OR EQUAL TO", "LESS-THAN OR SLANTED EQUAL TO"]:
            result += "<="
        elif name in ["GREATER-THAN OR EQUAL TO", "GREATER-THAN OR SLANTED EQUAL TO"]:
            result += ">="
        else:
            result += char

        prev_name = name
    return result


#####
# Customised SymPy Internals:
#####

# What constitutes a relation?
RELATIONS = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}


def evaluateFalse(s):
    """Replaces operators with the SymPy equivalents and set evaluate=False.

       Unlike the built-in evaluateFalse(...), we want to use a slightly more
       sophisticated EvaluateFalseTransformer and make operators AND functions
       evaluate=False.
        - 's' should be a string of Python code for the maths abstract syntax tree.
    """
    node = ast.parse(s)
    node = _EvaluateFalseTransformer().visit(node)
    # node is a Module, we want an Expression
    node = ast.Expression(node.body[0].value)

    return ast.fix_missing_locations(node)


class _EvaluateFalseTransformer(sympy_parser.EvaluateFalseTransformer):
    """Extend default SymPy EvaluateFalseTransformer to affect functions too.

       The SymPy version does not force function calls to be 'evaluate=False',
       which means expressions like "log(x, 10)" get simplified to "log(x)/log(10)"
       or "cos(-x)" becomes "cos(x)". For our purposes, this is unhelpful and so
       we also prevent this from occuring.

       Currently there is a list of functions not to transform, because some do
       not support the "evaluate=False" argument. This isn't particularly nice or
       future proof!
    """

    _evaluate_false_keyword = ast.keyword(arg='evaluate', value=ast.Name(id='False', ctx=ast.Load()))
    _bool_ops = {
        ast.And: "And",
        ast.Or: "Or"
    }


    def visit_Call(self, node):
        """Ensure all function calls are 'evaluate=False'."""
        # Since we have overridden the visit method, we are now responsible for
        # ensuring all child nodes are visited too. This is done most simply by
        # calling generic_visit(...) on ourself:
        self.generic_visit(node)
        # FIXME: Some functions cannot accept "evaluate=False" as an argument
        # without their __new__() method raising a TypeError. There is probably
        # some underlying reason which we could take into account of.
        # For now, blacklist those known to be problematic:
        _ignore_functions = ["Integer", "Float", "Symbol", "factorial", "sqrt", "Sqrt"]
        if node.func.id in _ignore_functions:
            # print "\tIgnoring function: {}".format(node.func.id)
            pass
        else:
            # print "\tModifying function: {}".format(node.func.id)
            node.keywords.append(self._evaluate_false_keyword)
        # We must return the node, modified or not:
        return node

    def visit_Compare(self, node):
        """Ensure all comparisons use sympy classes with 'evaluate=False'."""
        # Can't cope with comparing multiple inequalities:
        if len(node.comparators) > 1:
            raise TypeError("Cannot parse nested inequalities!")
        # As above, must ensure child nodes are visited:
        self.generic_visit(node)
        # Use the custom Equals class if equality, otherwise swap with a know relation:
        operator_class = node.ops[0].__class__
        if isinstance(node.ops[0], ast.Eq):
            return ast.Call(func=ast.Name(id='Eq', ctx=ast.Load()), args=[node.left, node.comparators[0]], keywords=[self._evaluate_false_keyword])
        elif operator_class in RELATIONS:
            return ast.Call(func=ast.Name(id='Rel', ctx=ast.Load()), args=[node.left, node.comparators[0], ast.Str(RELATIONS[operator_class])], keywords=[self._evaluate_false_keyword])
        else:
            # An unknown type of relation. Leave alone:
            return node

#    def visit(self, node):
#        """Visit every node in the tree."""
#        print(ast.dump(node))
#        self.generic_visit(node)
#        return node

#####
# Custom SymPy Parser Transformations:
#####

def auto_symbol(tokens, local_dict, global_dict):
    """Replace the sympy builtin auto_symbol with a much more aggressive version.

       We have to replace this, because SymPy attempts to be too accepting of
       what it considers to be valid input and allows Pythonic behaviour.
       We only really want pure mathematics notations where possible!
    """
    result = []
    # As with all tranformations, we have to iterate through the tokens and
    # return the modified list of tokens:
    for tok in tokens:
        tokNum, tokVal = tok
        if tokNum == tokenize.NAME:
            name = tokVal
            # Check if the token name is in the local/global dictionaries.
            # If it is, convert it correctly, otherwise leave untouched.
            if name in local_dict:
                result.append((tokenize.NAME, name))
                continue
            elif name in global_dict:
                obj = global_dict[name]
                if isinstance(obj, (Basic, type)) or callable(obj):
                    # If it's a function/basic class, don't convert it to a Symbol!
                    result.append((tokenize.NAME, name))
                    continue
            result.extend([
                (tokenize.NAME, 'Symbol'),
                (tokenize.OP, '('),
                (tokenize.NAME, repr(str(name))),
                (tokenize.OP, ')'),
            ])
        else:
            result.append((tokNum, tokVal))

    return result


def split_symbols_implicit_precedence(tokens, local_dict, global_dict):
    """Replace the sympy builtin split_symbols with a version respecting implicit multiplcation.

       By replacing this we can better cope with expressions like 1/xyz being
       equivalent to 1/(x*y*z) rather than (y*z)/x as is the default. However it
       cannot address issues like 1/2x becoming (1/2)*x rather than 1/(2*x), because
       Python's tokeniser does not respect whitespace and so cannot distinguish
       between '1/2 x' and '1/2x'.

       This transformation is unlikely to be used, but is provided as proof of concept.
    """
    result = []
    split = False
    split_previous = False
    for tok in tokens:
        if split_previous:
            # throw out closing parenthesis of Symbol that was split
            split_previous = False
            continue
        split_previous = False
        if tok[0] == tokenize.NAME and tok[1] == 'Symbol':
            split = True
        elif split and tok[0] == tokenize.NAME:
            symbol = tok[1][1:-1]
            if sympy_parser._token_splittable(symbol):
                # If we're splitting this symbol, wrap it in brackets by adding
                # them before the call to Symbol:
                result = result[:-2] + [(tokenize.OP, '(')] + result[-2:]
                for char in symbol:
                    if char in local_dict or char in global_dict:
                        # Get rid of the call to Symbol
                        del result[-2:]
                        result.extend([(tokenize.NAME, "{}".format(char)),
                                       (tokenize.NAME, 'Symbol'), (tokenize.OP, '(')])
                    else:
                        result.extend([(tokenize.NAME, "'{}'".format(char)), (tokenize.OP, ')'),
                                       (tokenize.NAME, 'Symbol'), (tokenize.OP, '(')])
                # Delete the last two tokens: get rid of the extraneous
                # Symbol( we just added
                # Also, set split_previous=True so will skip
                # the closing parenthesis of the original Symbol
                del result[-2:]
                split = False
                split_previous = True
                # Then close the extra brackets we added:
                result.append((tokenize.OP, ')'))
                continue
            else:
                split = False
        result.append(tok)
    return result
