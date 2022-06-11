# -*- coding: utf-8 -*-

import unittest

from checker.parsing import maths_parser, logic_parser
from checker import maths as api


#####
# Test parsing module functions:
#####
class TestMathsParsing(unittest.TestCase):

    def test_cleanup_string(self):
        print("\n\n\n" + " Test cleanup_string(...) Function ".center(75, "#"))
        strings = ["().__class__.__bases__[0]", "().__class__", "(lambda:0).func_code", "__",
                   "eval('()._' + '_class_' + '_._' + '_bases_' + '_[0]')",
                   "5.a", "\u2622 \U0001F4A9", "x = 5", "lambda x: 2*x", "[1, 2, 3]"]

        for s in strings:
            # These strings should not be left unmodified by cleanup_string:
            clean_s = maths_parser.cleanup_string(s, reject_unsafe_input=False)
            print("Unsafe input  : '{}'".format(s))
            print("Cleaner input : '{}'".format(clean_s))
            equal = (clean_s == s)
            self.assertFalse(equal)
            print(" - - - ")
        print("Known unsafe strings sanitised slightly.")
        print("   PASS   ".center(75, "#"))

    def test_is_valid_symbol(self):
        print("\n\n\n" + " Test cleanup_string(...) Function ".center(75, "#"))
        valid_symbols = ["x", "DeltaX", "Phi", "Omega", "alpha"]
        invalid_symbols = ["", "_trigs", "_logs", "sin()", "cos()", "_no_alphabet"]

        test_valid_symbols = list(map(maths_parser.is_valid_symbol, valid_symbols))
        print("Valid symbols parsed:   {}".format(test_valid_symbols))
        test_invalid_symbols = list(map(maths_parser.is_valid_symbol, invalid_symbols))
        print("Invalid symbols parsed: {}".format(test_invalid_symbols))

        self.assertTrue(all(test_valid_symbols), "Expected all valid symbols to pass!")
        self.assertFalse(any(test_invalid_symbols), "Expect all invalid symbols to fail!")
        print("Known non-symbols skipped correctly!")
        print("   PASS   ".center(75, "#"))

    def test_long_notation_ignored(self):
        print("\n\n\n" + " Test Long Notation is Ignored ".center(75, "#"))
        from sympy import log
        test_str = "2L + 2log(2)"

        test_expr = api.parse_expression(test_str)
        print("Test expression: '{}'".format(test_expr))

        self.assertTrue(len(test_expr.free_symbols) > 0, "Expected '2L' to parse as '2*L' not '2'!")
        print("Expression has symbols:   {}".format(test_expr.free_symbols))
        self.assertTrue(test_expr.has(log), "Expected expression to contain a logarithm!")
        print("Long integer notation ignored successfully!")
        print("   PASS   ".center(75, "#"))

    def test_parse_hints(self):
        print("\n\n\n" + " Test Parse Hints Used ".center(75, "#"))
        test_str = "e**(i * pi)"
        parse_hints = ["constant_pi", "constant_e", "imaginary_i"]

        test_expr = maths_parser.parse_expr(test_str, hints=parse_hints)
        print("Test expression: '{}'".format(test_expr))

        self.assertTrue(len(test_expr.free_symbols) == 0, "Expected 'e', 'pi' and 'i' to parse specially!")
        print("Expression has symbols:   {}".format(test_expr.free_symbols))
        print("   PASS   ".center(75, "#"))

    def test_unicode_substitution(self):
        print("\n\n\n" + " Test cleanup_string(...) Swaps Unicode ".center(75, "#"))
        maths_values = {
            "\u00BD": "(1/2)",
            "a\u00B2 + b\u00B9\u2070": "a**2 + b**10",
            "v\u2081 + v\u2081\u2081": "v_1 + v_11",
            "\u00D7": "*",
            "\u00F7": "/",
            "\u003C \u003E": "< >",
            "\u2264 \u2265": "<= >=",
        }
        logic_values = {
            "\u2227 \u2228": "& |",
            "\u00AC": "~",
            "\u22BB": "^",
        }
        greek_letters = {
            "\u03C0": "pi",
            "\u0398": "Theta",
        }

        for unicode_str, replacement in maths_values.items():
            clean_s = maths_parser.cleanup_string(unicode_str, reject_unsafe_input=False)
            print("Unicode input: '{}'".format(unicode_str))
            print("Equivalent   : '{}'".format(clean_s))
            self.assertEqual(clean_s, replacement)
            print(" - - - ")
        for unicode_str, replacement in logic_values.items():
            clean_s = logic_parser.cleanup_string(unicode_str, reject_unsafe_input=False)
            print("Unicode input: '{}'".format(unicode_str))
            print("Equivalent   : '{}'".format(clean_s))
            self.assertEqual(clean_s, replacement)
            print(" - - - ")
        for unicode_str, replacement in greek_letters.items():
            clean_s = maths_parser.cleanup_string(unicode_str, reject_unsafe_input=False)
            print("Unicode input: '{}'".format(unicode_str))
            print("Equivalent   : '{}'".format(clean_s))
            self.assertTrue(unicode_str not in clean_s)
            self.assertTrue(replacement in clean_s)
        print("Unicode replaced with ASCII equivalents.")
        print("   PASS   ".center(75, "#"))


if __name__ == '__main__':
    unittest.main()
