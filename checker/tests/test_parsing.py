# -*- coding: utf-8 -*-

import unittest

from checker.parsing import maths_parser as parsing
from checker import maths as api


#####
# Test parsing module functions:
#####
class TestParsing(unittest.TestCase):

    def test_cleanup_string(self):
        print("\n\n\n" + " Test cleanup_string(...) Function ".center(75, "#"))
        strings = ["().__class__.__bases__[0]", "().__class__", "(lambda:0).func_code", "__",
                   "eval('()._' + '_class_' + '_._' + '_bases_' + '_[0]')",
                   "5.a", "\u2622 \U0001F4A9", "x = 5", "lambda x: 2*x", "[1, 2, 3]"]

        for s in strings:
            # These strings should not be left unmodified by cleanup_string:
            clean_s = parsing.cleanup_string(s, reject_unsafe_input=False)
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

        test_valid_symbols = list(map(parsing.is_valid_symbol, valid_symbols))
        print("Valid symbols parsed:   {}".format(test_valid_symbols))
        test_invalid_symbols = list(map(parsing.is_valid_symbol, invalid_symbols))
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


if __name__ == '__main__':
    unittest.main()
