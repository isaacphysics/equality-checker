import unittest

from checker import logic as api
from checker.utils import EqualityType
from checker.parsing import logic_parser as parsing

EQUALITY_TYPES = [t.value for t in EqualityType if t is not EqualityType.KNOWN]


#####
# These tests check behavior for very simple cases, and for complicated cases
# where exact matching is important.
#####
class TestFundamentals(unittest.TestCase):

    def test_symbols_equal(self):
        print("\n\n\n" + " Test if Symbols can be Equal ".center(75, "#"))
        test_str = "P"
        target_str = "P"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_and(self):
        print("\n\n\n" + " Test if AND (&) Works ".center(75, "#"))
        test_str = "P & Q"
        target_str = "Q & P"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_or(self):
        print("\n\n\n" + " Test if OR (|) Works ".center(75, "#"))
        test_str = "P | Q"
        target_str = "Q | P"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_not(self):
        print("\n\n\n" + " Test if NOT (~) Works ".center(75, "#"))
        test_str = "~P"
        target_str = "~P"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_xor(self):
        print("\n\n\n" + " Test if XOR (^) Works ".center(75, "#"))
        test_str = "P ^ Q"
        target_str = "(P & ~Q) | (Q & ~P)"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_equivalence(self):
        print("\n\n\n" + " Test if Equivalence (==) Works ".center(75, "#"))
        test_str = "P == Q"
        target_str = "Q == P"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_implies(self):
        print("\n\n\n" + " Test if Implies (>>) Works ".center(75, "#"))
        test_str = "P >> Q"
        target_str = "P >> Q"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_demorgan_and(self):
        print("\n\n\n" + " Test De Morgan's Law (AND) ".center(75, "#"))
        test_str = "~(A & B)"
        target_str = "~A | ~B"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_demorgan_or(self):
        print("\n\n\n" + " Test De Morgan's Law (OR) ".center(75, "#"))
        test_str = "~(A | B)"
        target_str = "~A & ~B"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_not_not(self):
        print("\n\n\n" + " Test NOT NOT Cancellation ".center(75, "#"))
        test_str = "~~A"
        target_str = "A"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "{}"!'.format(response["equality_type"]))
        print("   PASS   ".center(75, "#"))

    def test_no_simplification(self):
        print("\n\n\n" + " Test No Simplification ".center(75, "#"))
        test_str = "A and ~A"
        result = api.parse_expression(test_str)

        self.assertTrue(len(result.free_symbols) == 1, 'Expected variable in result!')
        print("   PASS   ".center(75, "#"))

    def test_true_and_false(self):
        print("\n\n\n" + " Test True and False ".center(75, "#"))
        test_str = "not False"
        target_str = "True"
        symbols = None
        response = api.check(test_str, target_str, symbols=symbols)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "true", 'Expected "equal" to be "true", got "{}"!'.format(response["equal"]))
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
        test_str = "().__class__.__blah__"
        target_str = "A"
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        print("   PASS   ".center(75, "#"))

    def test_invalid_target(self):
        print("\n\n\n" + " Test if Invalid Target Detected ".center(75, "#"))
        test_str = "A & B"
        target_str = "A & B & "
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("code" in response, 'Expected "code" in response!')
        self.assertTrue(response["code"] == 400, 'Expected error "code" 400 in response, got "{}"!'.format(response["code"]))
        print("   PASS   ".center(75, "#"))

    def test_invalid_test_str(self):
        print("\n\n\n" + " Test if Invalid Test Str Detected ".center(75, "#"))
        test_str = "A & B & "
        target_str = "A & B"
        response = api.check(test_str, target_str)

        # Implicitly we're testing no unhandled exceptions.
        self.assertTrue("error" in response, 'Expected "error" in response!')
        self.assertTrue("code" not in response, 'Expected "code" in response!')
        print("   PASS   ".center(75, "#"))

    def test_missing_symbols(self):
        print("\n\n\n" + " Test if Missing Symbols Detected ".center(75, "#"))
        test_str = "A"
        target_str = "B"
        response = api.check(test_str, target_str, check_symbols=True)

        self.assertTrue("error" not in response, 'Unexpected "error" in response!')
        self.assertTrue("equal" in response, 'Key "equal" not in response!')
        self.assertTrue(response["equal"] == "false", 'Expected "equal" to be "false", got "{}"!'.format(response["equal"]))
        self.assertTrue("equality_type" in response, 'Key "equality_type" not in response!')
        self.assertTrue(response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "{}"!'.format(response["equality_type"]))
        self.assertTrue(response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "exact", got "{}"!'.format(response["equality_type"]))
        self.assertTrue("incorrect_symbols" in response, 'Key "incorrect_symbols" not in response!')
        print("   PASS   ".center(75, "#"))


if __name__ == '__main__':
    unittest.main()
