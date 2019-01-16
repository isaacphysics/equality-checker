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
        target_str = "P & Q"
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
        target_str = "P | Q"
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

    def test_equlvalence(self):
        print("\n\n\n" + " Test if Equivalence (==) Works ".center(75, "#"))
        test_str = "P == Q"
        target_str = "P == Q"
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


if __name__ == '__main__':
    unittest.main()
