from enum import Enum


class EqualityType(Enum):
    KNOWN = "known"
    NUMERIC = "numeric"
    SYMBOLIC = "symbolic"
    EXACT = "exact"


def known_equal_pair(known_pairs, test_expr, target_expr):
    """In lieu of any real persistent cache of known pairs, just use a dict for now!

       Checks if the two expressions are known pairs from previous testing; this
       should reduce calls to 'simplify' and the numeric testing, both of which
       are computationally costly and slow.
    """
    print("[[KNOWN PAIR CHECK]]")
    pair = (target_expr, test_expr)
    if pair in known_pairs:
        print("Known Pair from {} equality!".format(known_pairs[pair].value))
        return (True, known_pairs[pair])
    else:
        return (False, EqualityType.KNOWN)


def contains_incorrect_symbols(test_expr, target_expr):
    """Test if the entered expression contains exactly the same symbols as the target.

       Sometimes expressions can be mathematically identical to one another, but
       contain different symbols. From a pure maths standpoint, this is fine; but
       in questions you may not want to allow undefined symbols. This function will
       return a dict containing entries for any extra/missing symbols.
        - 'test_expr' should be the untrusted sympy expression to check symbols from.
        - 'target_expr' should be the trusted sympy expression to match symbols to.
    """
    print("[[SYMBOL CHECK]]")
    if test_expr.free_symbols != target_expr.free_symbols:
        print("Symbol mismatch between test and target!")
        result = dict()
        missing = ",".join(map(str, list(target_expr.free_symbols.difference(test_expr.free_symbols))))
        extra = ",".join(map(str, list(test_expr.free_symbols.difference(target_expr.free_symbols))))
        missing = missing.replace("lamda", "lambda").replace("Lamda", "Lambda")
        extra = extra.replace("lamda", "lambda").replace("Lamda", "Lambda")
        if len(missing) > 0:
            print("Test Expression missing: {}".format(missing))
            result["missing"] = missing
        if len(extra) > 0:
            print("Test Expression has extra: {}".format(extra))
            result["extra"] = extra
        print("Not Equal: Enforcing strict symbol match for correctness!")
        return result
    else:
        return None


def eq_type_order(eq_types):
    """Return the worst equality type from a list of equality types.

       Useful for indicating what type of match an equation or relation has: give
       the worst possible type since this is the weakest link in the equality checking.
    """
    if EqualityType.NUMERIC in eq_types:
        return EqualityType.NUMERIC
    elif EqualityType.SYMBOLIC in eq_types:
        return EqualityType.SYMBOLIC
    elif EqualityType.EXACT in eq_types:
        return EqualityType.EXACT
    else:
        raise TypeError("Unexpected list of equality types: {}".format(eq_types))
