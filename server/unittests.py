import api

EQUALITY_TYPES = ["exact", "symbolic", "numeric"]
FAILS = {}
tests = 0


def test1():
    global tests
    print "##### Test if Integers can be Equal #####"
    tests += 1
    test_str = "1"
    target_str = "1"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test2():
    global tests
    print "##### Test if Single Variables can be Equal #####"
    tests += 1
    test_str = "x"
    target_str = "x"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test3():
    global tests
    print "##### Test if Addition Order matters for Exact Match #####"
    tests += 1
    test_str = "1 + x"
    target_str = "x + 1"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test4():
    global tests
    print "##### Test if Integers can be found Unequal #####"
    tests += 1
    test_str = "2"
    target_str = "1"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "false", 'Expected "equal" to be "false", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
#        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test5():
    global tests
    print "##### Test if Two Single Variables can be found Unequal #####"
    tests += 1
    test_str = "x"
    target_str = "y"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "false", 'Expected "equal" to be "false", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
#        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test6():
    global tests
    print "##### Test that Simple Brackets are Ignored for Exact Match #####"
    tests += 1
    test_str = "((x))"
    target_str = "x"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test7():
    global tests
    print "##### Test that Variable Ordering is Ignored for Exact Match #####"
    tests += 1
    test_str = "x * y * z"
    target_str = "z * x * y"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test8():
    global tests
    print "##### Test that Implicit Multiplication Works #####"
    tests += 1
    test_str = "xyz"
    target_str = "x * y * z"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test9():
    global tests
    print "##### Test Bracket Ordering is Ignored for Exact Match #####"
    tests += 1
    test_str = "(x + 1)(x + 2)"
    target_str = "(x + 2)(x + 1)"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test10():
    global tests
    print "##### Test Fractions Work for Exact Match #####"
    tests += 1
    test_str = "x*(1/y)"
    target_str = "x/y"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "exact", 'For these expressions, expected "equality_type" to be "exact", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test11():
    global tests
    print "##### Test Fractions can be Simplified for Symbolic not Exact Match #####"
    tests += 1
    test_str = "(2*x*y*x)/(2*x*y*y)"
    target_str = "x/y"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test12():
    global tests
    print "##### Test Brackets can be Expanded and Simplified for Symbolic Match #####"
    tests += 1
    test_str = "(x + 1)(x + 1)"
    target_str = "x**2 + 2*x + 1"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" not in response, 'Unexpected "error" in response: "%s"!' % response["error"]
        assert "equal" in response, 'Key "equal" not in response!'
        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
        assert "equality_type" in response, 'Key "equality_type" not in response!'
        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
        assert response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


def test13():
    global tests
    print "##### Test Factorials are correctly Limited #####"
    tests += 1
    test_str = "factorial(1000)"
    target_str = "1"
    symbols = None
    response = api.check(test_str, target_str, symbols)

    print "#####     TEST RESULT:     #####"
    try:
        assert "error" in response, 'Unexpected lack of "error" in response!'
        assert response["error"] == "Parsing Test Expression Failed: '[Factorial]: Too large integer to compute factorial effectively!'", "Error message not as expected '%s'." % response["error"]
#        assert "equal" in response, 'Key "equal" not in response!'
#        assert response["equal"] == "true", 'Expected "equal" to be "true", got "%s"!' % response["equal"]
#        assert "equality_type" in response, 'Key "equality_type" not in response!'
#        assert response["equality_type"] in EQUALITY_TYPES, 'Unexpected "equality_type": "%s"!' % response["equality_type"]
#        assert response["equality_type"] == "symbolic", 'For these expressions, expected "equality_type" to be "symbolic", got "%s"!' % response["equality_type"]
        print "PASS"
        return True
    except AssertionError as e:
        print "FAIL: '%s'" % e.message
        FAILS[(target_str, test_str)] = e.message
        return False


test1()
print "\n"
test2()
print "\n"
test3()
print "\n"
test4()
print "\n"
test5()
print "\n"
test6()
print "\n"
test7()
print "\n"
test8()
print "\n"
test9()
print "\n"
test10()
print "\n"
test11()
print "\n"
test12()
print "\n"
test13()

print "\n\n\n" + "#" * 50
print "   Test Results   ".center(50, "#")
print "#" * 50
print "Testing Finished: %s of %s passed, %s failed." % (tests - len(FAILS), tests, len(FAILS))
print ""
for f in FAILS:
    print "Test Failed:\n\t'%s' == '%s'" % f
    print "Error: %s\n" % FAILS[f]
