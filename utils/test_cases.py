import sys
import os
import json
import pytest

# Hack to allow using the "checker" module from the parent folder without
# installing it globally:
sys.path.insert(0, '..')

from checker import maths, logic

# The JSON file is always next to this file, so open it using __file__'s path:
testcases_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_cases.json")
with open(testcases_filepath) as testcases_file:
    test_cases = json.load(testcases_file)


pytest_cases = []

for test_case, test_details in test_cases.items():
    for test_value in test_details["shouldMatch"]:
        pytest_cases.append((test_details["type"], test_case, test_value, test_details["requireExact"]))


@pytest.mark.parametrize("checker_type,target_str,test_str,exact", pytest_cases)
def test_eval(checker_type, target_str, test_str, exact):
    if checker_type == "maths":
        result = maths.check(test_str, target_str)
    elif checker_type == "logic":
        result = logic.check(test_str, target_str)
    else:
        raise ValueError("Unknown checker: {}".format(checker_type))
    # Test equality:
    assert result["equal"] == "true"

    # Test match type:
    if exact:
        assert result["equality_type"] == "exact"
