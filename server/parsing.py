# Copyright 2017 James Sharkey
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

import sympy
import sympy.abc
from sympy.parsing import sympy_parser, sympy_tokenize
from sympy.core.numbers import Integer, Float, Rational
from sympy.core.basic import Basic
import ast
import re


RELATIONS_REGEX = '(.*?)(==|<=|>=|<|>)(.*)'


#####
# Custom Symbol / Function / Operator Classes:
#####


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
        raise ValueError("[Factorial]: Too large integer to compute factorial effectively!")
    else:
        return sympy.factorial(n)


#####
# Custom SymPy Parser Transformations:
#####


def auto_symbol(tokens, local_dict, global_dict):
    """Replace the sympy builtin auto_symbol with a much more aggressive version.

       We have to replace this, because SymPy attempts to be too accepting of
       what it considers to be valid input and allows Pythonic behaviour.
       We only really want pure mathematics notations where possible!"""
    result = []
    # As with all tranformations, we have to iterate through the tokens and
    # return the modified list of tokens:
    for tok in tokens:
        tokNum, tokVal = tok
        if tokNum == sympy_tokenize.NAME:
            name = tokVal
            # Check if the token name is in the local/global dictionaries.
            # If it is, convert it correctly, otherwise leave untouched.
            if name in local_dict:
                result.append((sympy_tokenize.NAME, name))
                continue
            elif name in global_dict:
                obj = global_dict[name]
                if isinstance(obj, (Basic, type)) or callable(obj):
                    # If it's a function/basic class, don't convert it to a Symbol!
                    result.append((sympy_tokenize.NAME, name))
                    continue
            result.extend([
                (sympy_tokenize.NAME, 'Symbol'),
                (sympy_tokenize.OP, '('),
                (sympy_tokenize.NAME, repr(str(name))),
                (sympy_tokenize.OP, ')'),
            ])
        else:
            result.append((tokNum, tokVal))

    return result


#####
# Customised SymPy Internals:
#####


def evaluateFalse(s):
    """Replaces operators with the SymPy equivalents and set evaluate=False.

       Unlike the built-in evaluateFalse(...), we want to use a slightly more
       sophisticated EvaluateFalseTransformer and make operators AND functions
       evaluate=False.
        - 's' should be a string of Python code for the maths abstract syntax tree.
    """
    node = ast.parse(s)
    node = EvaluateFalseTransformer().visit(node)
    # node is a Module, we want an Expression
    node = ast.Expression(node.body[0].value)

    return ast.fix_missing_locations(node)


class EvaluateFalseTransformer(sympy_parser.EvaluateFalseTransformer):
    """Extend default SymPy EvaluateFalseTransformer to affect functions too.

       The SymPy version does not force function calls to be 'evaluate=False',
       which means expressions like "log(x, 10)" get simplified to "log(x)/log(10)"
       or "cos(-x)" becomes "cos(x)". For our purposes, this is unhelpful and so
       we also prevent this from occuring.

       Currently there is a list of functions not to transform, because some do
       not support the "evaluate=False" argument. This isn't particularly nice or
       future proof!
    """
    def visit_Call(self, node):
        # Since we have overridden the visit method, we are now responsible for
        # ensuring all child nodes are visited too. This is done most simply by
        # calling generic_visit(...) on ourself:
        self.generic_visit(node)
        # FIXME: Some functions cannot accept "evaluate=False" as an argument
        # without their __new__() method raising a TypeError. There is probably
        # some underlying reason which we could take into account of.
        # For now, blacklist those known to be problematic:
        _ignore_functions = ["Integer", "Float", "Symbol", "factorial", "sqrt"]
        if node.func.id in _ignore_functions:
            # print "\tIgnoring function: %s" % node.func.id
            pass
        else:
            # print "\tModifying function: %s" % node.func.id
            node.keywords.append(ast.keyword(arg='evaluate', value=ast.Name(id='False', ctx=ast.Load())))
        # We must return the node, modified or not:
        return node


#####
# Custom Parsers:
#####

# These constants are needed to address some security issues.
# We don't want to use the default transformations, and we need to use a
# whitelist of functions the parser should allow to match.
_TRANSFORMS = (sympy.parsing.sympy_parser.auto_number, auto_symbol,
               sympy.parsing.sympy_parser.convert_xor, sympy_parser.split_symbols, sympy_parser.implicit_multiplication)

_GLOBAL_DICT = {"Symbol": sympy.Symbol, "Integer": sympy.Integer, "Float": sympy.Float, "Rational": sympy.Rational,
                "Mul": sympy.Mul, "Pow": sympy.Pow, "Add": sympy.Add,
                "iI": sympy.I, "piPI": sympy.pi, "eE": sympy.E,
                "Rel": sympy.Rel, "Eq": Equal,
                "Derivative": sympy.Derivative, "diff": sympy.Derivative,
                "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
                "arcsin": sympy.asin, "arccos": sympy.acos, "arctan": sympy.atan,
                "sinh": sympy.sinh, "cosh": sympy.cosh, "tanh": sympy.tanh,
                "cosec": sympy.csc, "sec": sympy.sec, "cot": sympy.cot,
                "arccosec": sympy.acsc, "arcsec": sympy.asec, "arccot": sympy.acot,
                "cosech": sympy.csch, "sech": sympy.sech, "coth": sympy.coth,
                "exp": sympy.exp, "log": sympy.log, "ln": sympy.ln,
                "factorial": factorial,
                "sqrt": sympy.sqrt, "abs": sympy.Abs}


def _replace_relations(match_object):
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


def parse_expr(expression_str, transformations=_TRANSFORMS, local_dict=None, global_dict=_GLOBAL_DICT):
    """A clone of sympy.sympy_parser.parse_expr(...) which prevents all evaluation.

       This is almost a direct copy of the SymPy code, but it also converts inline
       relations like "==" or ">=" to the Relation class to prevent evaluation.

    """
    if local_dict is None:
        local_dict = {}
    expression_str = re.sub(RELATIONS_REGEX, _replace_relations, expression_str)  # To ensure not evaluated, swap relations with Rel class
    code = sympy_parser.stringify_expr(expression_str, local_dict, global_dict, transformations)
    ef_code = evaluateFalse(code)
    code_compiled = compile(ef_code, '<string>', 'eval')
    return sympy_parser.eval_expr(code_compiled, local_dict, global_dict)
