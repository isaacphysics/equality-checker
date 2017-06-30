from sympy.parsing import sympy_parser
import ast
import re


RELATIONS_REGEX = '(.*?)(==|<=|>=|<|>)(.*)'


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


def parse_expr(expression_str, transformations=sympy_parser.standard_transformations, local_dict=None, global_dict=None):
    """A clone of sympy.sympy_parser.parse_expr(...) which prevents all evaluation.

       This is almost a direct copy of the SymPy code, but it also converts inline
       relations like "==" or ">=" to the Relation class to prevent evaluation.

    """
    expression_str = re.sub(RELATIONS_REGEX, parse_relations, expression_str)  # To ensure not evaluated, swap relations with Rel class
    code = sympy_parser.stringify_expr(expression_str, local_dict, global_dict, transformations)
    ef_code = evaluateFalse(code)
    code_compiled = compile(ef_code, '<string>', 'eval')
    return sympy_parser.eval_expr(code_compiled, local_dict, global_dict)
