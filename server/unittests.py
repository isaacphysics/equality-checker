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

import unittest
import api

EQUALITY_TYPES = ["exact", "symbolic", "numeric"]


class TestEqualityChecker(unittest.TestCase):

    def test_integers_equal(self):
        print "\n\n\n" + " Test if Integers can be Equal ".center(75, "#")
        test_str = "1"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_single_variables_equal(self):
        print "\n\n\n" + " Test if Single Variables can be Equal ".center(75, "#")
        test_str = "x"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_addition_order_exact_match(self):
        print "\n\n\n" + " Test if Addition Order matters for Exact Match ".center(75, "#")
        test_str = "1 + x"
        target_str = "x + 1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_integers_unequal(self):
        print "\n\n\n" + " Test if Integers can be found Unequal ".center(75, "#")
        test_str = "5"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_single_variables_unequal(self):
        print "\n\n\n" + " Test if Two Single Variables can be found Unequal ".center(75, "#")
        test_str = "x"
        target_str = "y"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_simple_brackets_ignored_exact(self):
        print "\n\n\n" + " Test that Simple Brackets are Ignored for Exact Match ".center(75, "#")
        test_str = "((x))"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_variable_ordering_ignored_exact(self):
        print "\n\n\n" + " Test that Variable Ordering is Ignored for Exact Match ".center(75, "#")
        test_str = "x * y * z"
        target_str = "z * x * y"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_implicit_multiplication(self):
        print "\n\n\n" + " Test that Implicit Multiplication Works ".center(75, "#")
        test_str = "xyz"
        target_str = "x * y * z"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_bracket_ordering_ignored_exact(self):
        print "\n\n\n" + " Test Bracket Ordering is Ignored for Exact Match ".center(75, "#")
        test_str = "(x + 1)(x + 2)"
        target_str = "(x + 2)(x + 1)"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_fractions_exact_match(self):
        print "\n\n\n" + " Test Fractions Work for Exact Match ".center(75, "#")
        test_str = "x*(1/y)"
        target_str = "x/y"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_simplify_fractions_symbolic(self):
        print "\n\n\n" + " Test Fractions can be Simplified for Symbolic not Exact Match ".center(75, "#")
        test_str = "(2*x*y*x)/(2*x*y*y)"
        target_str = "x/y"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_brackets_expand_symbolic(self):
        print "\n\n\n" + " Test Brackets can be Expanded for Symbolic Match ".center(75, "#")
        test_str = "(x + 1)(x + 1)"
        target_str = "x**2 + 2*x + 1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_factorials_limited(self):
        print "\n\n\n" + " Test Factorials are correctly Limited ".center(75, "#")
        test_str = "factorial(1000)"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" in response, 'Unexpected lack of "error" in response!')
        self.assertTrue(response["error"] == "Parsing Test Expression Failed.", "Error message not as expected '%s'." % response["error"])
        print "   PASS   ".center(75, "#")

    def test_extra_test_variables(self):
        print "\n\n\n" + " Test N+1 Variable Test Expression ".center(75, "#")
        test_str = "sin(exp(sqrt(2*x)))**2 + cos(exp(sqrt(x))**sqrt(2))**2"
        target_str = "1"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "numeric", 'For these expressions, expected "equality_type" to be "numeric", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")

    def test_sqrt_x_squared(self):
        print "\n\n\n" + " Test Square Root of x Squared ".center(75, "#")
        test_str = "sqrt(x**2)"
        target_str = "x"
        symbols = None
        response = api.check(test_str, target_str, symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"])
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"])
        self.assertTrue(response["equality_type"] == "numeric", 'For these expressions, expected "equality_type" to be "numeric", got "%s"!' % response["equality_type"])
        print "   PASS   ".center(75, "#")


if __name__ == '__main__':
    unittest.main()
