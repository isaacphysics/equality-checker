# -*- coding: utf-8 -*-

import unittest

from checker import maths as api
from checker.utils import EqualityType

EQUALITY_TYPES = [t.value for t in EqualityType if t is not EqualityType.KNOWN]


#####
# These tests check behavior for very simple cases, and for complicated cases
# where exact matching is important.
#####
class TestExactMatching(unittest.TestCase):

    def test_integers_equal(self):
        print("\n\n\n" + " Test if Integers can be Equal ".center(75, "#"))
        test_str = "1"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_floats_equal(self):
        print("\n\n\n" + " Test if Decimal Numbers can be Equal ".center(75, "#"))
        test_str = " .765625059"
        target_str = "0.765625059"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_integers_unequal(self):
        print("\n\n\n" + " Test if Integers can be found Unequal ".center(75, "#"))
        test_str = "5"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_single_variables_equal(self):
        print("\n\n\n" + " Test if Single Variables can be Equal ".center(75, "#"))
        test_str = "x"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_addition_order_exact_match(self):
        print("\n\n\n" + " Test if Addition Order matters for Exact Match ".center(75, "#"))
        test_str = "1 + x"
        target_str = "x + 1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_single_variables_unequal(self):
        print("\n\n\n" + " Test if Two Single Variables can be found Unequal ".center(75, "#"))
        test_str = "x"
        target_str = "y"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols, check_symbols=False)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_simple_brackets_ignored_exact(self):
        print("\n\n\n" + " Test that Simple Brackets are Ignored for Exact Match ".center(75, "#"))
        test_str = "((x))"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_variable_ordering_ignored_exact(self):
        print("\n\n\n" + " Test that Variable Ordering is Ignored for Exact Match ".center(75, "#"))
        test_str = "x * y * z"
        target_str = "z * x * y"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_bracket_ordering_ignored_exact(self):
        print("\n\n\n" + " Test Bracket Ordering is Ignored for Exact Match ".center(75, "#"))
        test_str = "(x + 1)(x + 2)"
        target_str = "(x + 2)(x + 1)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_fractions_exact_match(self):
        print("\n\n\n" + " Test Fractions Work for Exact Match ".center(75, "#"))
        test_str = "x*(1/y)"
        target_str = "x/y"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_log_matching_not_exact(self):
        print("\n\n\n" + " Test log(x)/log(10) not Exact Match of log(x, 10) ".center(75, "#"))
        test_str = "log(x) / log(10)"
        target_str = "log(x, 10)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] != "exact", 'For these expressions, expected "equality_type" not to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_cos_minus_x_not_exact(self):
        print("\n\n\n" + " Test cos(-x) not Exact Match of cos(x) ".center(75, "#"))
        test_str = "cos(x)"
        target_str = "cos(-x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] != "exact", 'For these expressions, expected "equality_type" not to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_implicit_multiplication(self):
        print("\n\n\n" + " Test that Implicit Multiplication Works ".center(75, "#"))
        test_str = "xyz"
        target_str = "x * y * z"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_unary_minus_as_subtraction(self):
        print("\n\n\n" + " Test Unary Minus is Consistent ".center(75, "#"))
        test_str = "1 - 2*x"
        target_str = "-2*x + 1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_lone_unary_minus(self):
        print("\n\n\n" + " Test Lone Unary Minus is Consistent ".center(75, "#"))
        test_str = "-xyz"
        target_str = "-(xyz)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests check behavior around the standard sympy alegbraic rearrangement
# and simplification.
#####
class TestSymbolicMatching(unittest.TestCase):

    def test_simplify_fractions_symbolic(self):
        print("\n\n\n" + " Test Fractions can be Simplified for Symbolic not Exact Match ".center(75, "#"))
        test_str = "(2*x*y*x)/(2*x*y*y)"
        target_str = "x/y"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_brackets_expand_symbolic(self):
        print("\n\n\n" + " Test Brackets can be Expanded for Symbolic Match ".center(75, "#"))
        test_str = "(x + 1)(x + 1)"
        target_str = "x**2 + 2*x + 1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_sqrt_x_squared(self):
        print("\n\n\n" + " Test Square Root of x Squared ".center(75, "#"))
        test_str = "sqrt(x**2)"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_large_bracket_expression(self):
        print("\n\n\n" + " Test Lots of Brackets and ^ in Expression ".center(75, "#"))
        test_str = "720 + 1764 x + 1624 x^2 + 735 x^3 + 175 x^4 + 21 x^5 + x^6"
        target_str = "(x+1)(x+2)(x+3)(x+4)(x+5)(x+6)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_main_trig_functions_symbolic(self):
        print("\n\n\n" + " Test if sin, cos and tan and inverses Work Symbolically ".center(75, "#"))
        test_str = "arcsin(x) + arccos(x) + arctan(x) + sin(x)**2 + cos(x)**2 + tan(x)"
        target_str = "1 + tan(x) + arcsin(x) + arccos(x) + arctan(x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_main_trig_functions_capitalised_symbolic(self):
        print("\n\n\n" + " Test if Trig Functions Work with Title Case Names ".center(75, "#"))
        test_str = "ArcSin(x) + ArcCos(x) + ArcTan(x) + Sin(x)**2 + Cos(x)**2 + Tan(x)"
        target_str = "1 + tan(x) + arcsin(x) + arccos(x) + arctan(x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_logarithms(self):
        print("\n\n\n" + " Test if Logarithms Work ".center(75, "#"))
        test_str = "x*log(x)/log(10) + ln(3) + ln(2)"
        target_str = "log(x,10)*x + ln(6)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests investigate the `check_symbols` feature.
#####
class TestCheckSymbols(unittest.TestCase):

    def test_extra_test_variables(self):
        print("\n\n\n" + " Test N+1 Variable Test Expression ".center(75, "#"))
        test_str = "sin(exp(sqrt(2*x)))**2 + cos(exp(sqrt(x))**sqrt(2))**2"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols, check_symbols=False)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_disallowed_extra_variables(self):
        print("\n\n\n" + " Enforce Only Allowed Symbols ".center(75, "#"))
        test_str = "sin(exp(sqrt(2*x)))**2 + cos(exp(sqrt(x))**sqrt(2))**2"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols, check_symbols=True)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For enforced symbols, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests check that equations and inequalities can be entered and tested.
#####
class TestEquationAndInequalitySupport(unittest.TestCase):

    def test_equations(self):
        print("\n\n\n" + " Test if Equations Can be Parsed and Checked ".center(75, "#"))
        test_str = "x**2 + x + 1 == 0"
        target_str = "x + 1 + x**2 == 0"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_inequalities(self):
        print("\n\n\n" + " Test if Inequalities Can be Parsed and Checked ".center(75, "#"))
        test_str = "x**2 + x + 1 > 0"
        target_str = "0 < x + 1 + x**2"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_strict_inequalities(self):
        print("\n\n\n" + " Test if Strict Inequalities Can be Distinguished ".center(75, "#"))
        test_str = "x**2 + x + 1 > 0"
        target_str = "x + 1 + x**2 >= 0"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests check derivative behaviour, including whether they can be simplified,
# and checking that they are not simplified by default.
#####
class TestDerivativeSupport(unittest.TestCase):

    def setUp(self):
        # This must run for tearDown() to run . . .
        api.KNOWN_PAIRS = dict()  # Ensure that results aren't cached for these specific tests!

    def tearDown(self):
        # Ensure that we always set this back to False, even if tests fail!
        api.SIMPLIFY_DERIVATIVES = False

    def test_derivatives(self):
        print("\n\n\n" + " Test if Derivatives Work ".center(75, "#"))
        api.SIMPLIFY_DERIVATIVES = False
        test_str = "2 * Derivative(y, x) / 2"
        target_str = "Derivative(y, x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_differential_equations(self):
        print("\n\n\n" + " Test Differential Equations ".center(75, "#"))
        api.SIMPLIFY_DERIVATIVES = True
        test_str = "Derivative(Derivative(y, x), x) == y*cos(x) + sin(x)*Derivative(y, x)"
        target_str = "Derivative(y, x, x) == Derivative(sin(x) * y, x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_derivatives_can_be_simplified(self):
        print("\n\n\n" + " Test if Derivatives Can Be Simplified ".center(75, "#"))
        api.SIMPLIFY_DERIVATIVES = True
        test_str = "Derivative(cos(x)**2, x)"
        target_str = "-2 sin(x)cos(x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_derivatives_not_simplifed(self):
        print("\n\n\n" + " Test Derivatives Are Not Simplified ".center(75, "#"))
        test_str = "Derivative(cos(x)**2, x)"
        target_str = "-2 sin(x)cos(x)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "numeric", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests check behavior around symbols more complicated than single characters,
# including compound symbols using underscores and custom symbols.
#####
class TestSymbolParsingAndSplitting(unittest.TestCase):

    def test_keywords_not_special(self):
        print("\n\n\n" + " Test if Python Keywords are Ignored ".center(75, "#"))
        test_str = "2as + 4for + is + print"
        target_str = "2*a*s + 4*f*o*r + i*s + p*r*i*n*t"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_compound_symbols_accepted(self):
        print("\n\n\n" + " Test if Compound Symbols Work ".center(75, "#"))
        test_str = "v_zmf**(2) == v_x**2 + v_y**2"
        target_str = "v_zmf * v_zmf == v_x * v_x + v_y * v_y"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_custom_symbols_accepted(self):
        print("\n\n\n" + " Test if Custom Symbols Work ".center(75, "#"))
        test_str = "test == abcd / d"
        target_str = "test == abc"
        symbols = "test, abcd, abc"
        response = api.check(test_str, target_str, symbols=symbols, check_symbols=False)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        print("   PASS   ".center(75, "#"))


class TestOthers(unittest.TestCase):

    def test_plus_or_minus(self):
        print("\n\n\n" + " Test if The ± Symbol Works ".center(75, "#"))
        test_str = "a ± b"
        target_str = "a ± b"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_syntax_error(self):
        print("\n\n\n" + " Test if Syntax Errors are Reported ".center(75, "#"))
        test_str = "(a + b +"
        target_str = "a + b"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("syntax_error" in response, 'Key "syntax_error" not in response!')
        self.assertTrue(response["syntax_error"] == "true", 'Expected "syntax_error" to be "true", got "{}"!'.format(response["syntax_error"]))
        print("   PASS   ".center(75, "#"))

#    def test_factorials_limited(self):
#        print "\n\n\n" + " Test Factorials are correctly Limited ".center(75, "#")
#        test_str = "factorial(1000)"
#        target_str = "1"
#        symbols = None
#        response = api.check(test_str, target_str, symbols=symbols)
#
#        self.assertTrue("error" in response, 'Unexpected lack of "error" in response!')
#        self.assertTrue(response["error"] == "Parsing Test Expression Failed.", "Error message not as expected '{}'.".format(response["error"]))
#        print "   PASS   ".center(75, "#")


#####
# These tests are for specific parts of the main checking code and may more easily
# be broken by later modifications.
#####
class TestSubroutines(unittest.TestCase):

    def test_main_trig_functions_numeric(self):
        print("\n\n\n" + " Test if sin, cos and tan and inverses Work Numerically ".center(75, "#"))
        from sympy import symbols, sin, cos, tan, asin, acos, atan
        x, y = symbols('x,y')
        test_expr = sin(x) + cos(x) + tan(x) + asin(y) + acos(y) + atan(y)
        target_expr = sin(x) + cos(x) + tan(x) + asin(y) + acos(y) + atan(y)

        print("Target expression: '{}'".format(target_expr))
        print("Test expression: '{}'".format(test_expr))
        equal = api.numeric_equality(test_expr, target_expr)

        self.assertTrue(equal, "Expected expressions to be found numerically equal!")
        print("   PASS   ".center(75, "#"))

    def test_log_functions_numeric(self):
        print("\n\n\n" + " Test if log(x) and log(x, y) Work Numerically ".center(75, "#"))
        from sympy import symbols, log
        x, y = symbols('x,y')
        test_expr = log(x) + log(x, y, evaluate=False) + log(x)/log(y)
        target_expr = log(x) + 2 * log(x, y, evaluate=False)

        print("Target expression: '{}'".format(target_expr))
        print("Test expression: '{}'".format(test_expr))
        equal = api.numeric_equality(test_expr, target_expr)

        self.assertTrue(equal, "Expected expressions to be found numerically equal!")
        print("   PASS   ".center(75, "#"))

    def test_derivatives_numeric(self):
        print("\n\n\n" + " Test if Derivatives Work Numerically ".center(75, "#"))
        from sympy import symbols, Derivative
        x, y, z = symbols('x,y,z')
        test_expr = Derivative(y, x) + Derivative(z, x)
        target_expr = Derivative(z, x) + Derivative(y, x)

        print("Target expression: '{}'".format(target_expr))
        print("Test expression: '{}'".format(test_expr))
        equal = api.numeric_equality(test_expr, target_expr)

        self.assertTrue(equal, "Expected expressions to be found numerically equal!")
        print("   PASS   ".center(75, "#"))

    def test_extra_test_variables_numeric(self):
        print("\n\n\n" + " Test N+1 Variable Numeric Checking ".center(75, "#"))
        from sympy import symbols, exp, sin, cos, sqrt, Integer
        x = symbols('x')
        test_expr = sin(exp(sqrt(2*x)))**2 + cos(exp(sqrt(x))**sqrt(2))**2
        target_expr = Integer("1")
        symbols = None

        print("Target expression: '{}'".format(target_expr))
        print("Test expression: '{}'".format(test_expr))
        equal = api.numeric_equality(test_expr, target_expr)

        self.assertTrue(equal, "Expected expressions to be found numerically equal!")
        print("   PASS   ".center(75, "#"))

    def test_numeric_complexify(self):
        print("\n\n\n" + " Test if Complex-Number Sampling Works ".center(75, "#"))
        from sympy import asec
        test_expr = asec(0.1, evaluate=False)
        target_expr = asec(0.1, evaluate=False)

        print("Target expression: '{}'".format(target_expr))
        print("Test expression: '{}'".format(test_expr))
        equal = api.numeric_equality(test_expr, target_expr)

        self.assertTrue(equal, "Expected expressions to be found numerically equal!")
        print("   PASS   ".center(75, "#"))

    def test_numeric_range_issue(self):
        print("\n\n\n" + " Test if Numeric Range Checked ".center(75, "#"))
        test_str = "1/x"
        target_str = "1/x**20"
        response = api.check(test_str, target_str)

        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("Too Large Range" in response["error"], 'Expected warning about numeric range "{}"!'.format(response["error"]))
        print("   PASS   ".center(75, "#"))


#####
# These tests check the error behaviour when invalid values are passed.
#####
class TestErrorBehaviour(unittest.TestCase):

    def test_blank_input(self):
        print("\n\n\n" + " Test if Blank Input Detected ".center(75, "#"))
        test_str = ""
        target_str = "A"
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        print("   PASS   ".center(75, "#"))

    def test_unsafe_input(self):
        print("\n\n\n" + " Test if Unsafe Input Detected ".center(75, "#"))
        test_str = "A @ B"
        target_str = "A * B"
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        print("   PASS   ".center(75, "#"))

    def test_invalid_target(self):
        print("\n\n\n" + " Test if Invalid Target Detected ".center(75, "#"))
        test_str = "A + B"
        target_str = "A + B + "
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("code" in response, 'Expected "code" in response!')
        self.assertTrue(response["code"] == 400, 'Expected error "code" 400 in response, got "{}"!'.format(response["code"]))
        print("   PASS   ".center(75, "#"))

    def test_invalid_test_str(self):
        print("\n\n\n" + " Test if Invalid Test Str Detected ".center(75, "#"))
        test_str = "A + B + "
        target_str = "A + B"
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("code" not in response, 'Expected "code" in response!')
        print("   PASS   ".center(75, "#"))

    def test_missing_plus_minus(self):
        print("\n\n\n" + " Test Missing Plus-Minus Sign ".center(75, "#"))
        test_str = "A ± B"
        target_str = "A + B"
        response = api.check(test_str, target_str)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_invalid_plus_minus_values(self):
        print("\n\n\n" + " Test Invalid Plus-Minus Sign Result ".center(75, "#"))
        test_str = "x ± 1"
        target_str_1 = "x/(1 ± 1)"
        target_str_2 = "x/(1 ± -1)"
        response_1 = api.check(test_str, target_str_1)

        self.assertTrue("error" in response_1, 'Expected "error" in response!')
        self.assertTrue("case" in response_1, 'Key "case" not in response!')
        self.assertTrue(response_1["case"] == "-", 'Unexpected "case": "{}"!'.format(response_1["case"]))
        print("Negative case error correctly detected.")

        response_2 = api.check(test_str, target_str_2)

        self.assertTrue("error" in response_2, 'Expected "error" in response!')
        self.assertTrue("case" in response_2, 'Key "case" not in response!')
        self.assertTrue(response_2["case"] == "+", 'Unexpected "case": "{}"!'.format(response_2["case"]))
        print("Positive case error correctly detected.")
        print("   PASS   ".center(75, "#"))


if __name__ == '__main__':
    unittest.main()
