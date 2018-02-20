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


def is_number_times_variable(expr):
    try:
        assert expr.func.is_Mul
        assert len(expr.args) == 2
        if expr.args[0].is_Number:
            assert expr.args[1].is_Symbol
        elif expr.args[1].is_Number:
            assert expr.args[0].is_Symbol
        else:
            return False
        return True
    except AssertionError:
        return False


def is_pm_symbol_pm_num(expr):
    try:
        assert expr.func.is_Add
        assert len(expr.args) == 2
        if expr.args[0].is_Number:
            assert expr.args[1].is_Symbol or is_number_times_variable(expr.args[1])
        elif expr.args[1].is_Number:
            assert expr.args[0].is_Symbol or is_number_times_variable(expr.args[0])
        else:
            return False
        return True
    except AssertionError:
        return False


def is_factorised_polynomial(expr, n, prefactor=False):
    try:
        # Head of the tree should be multiplication:
        assert expr.func.is_Mul
        # Each branch should be to addition, or a factor:
        factors = 0
        for a in expr.args:
            if a.is_Add:
                assert is_pm_symbol_pm_num(a)
            else:
                factors += 1
        # If a prefactor is allowed, expect n + 1 branches:
        if prefactor:
            assert factors <= 1
            assert len(expr.args) - factors == n
        else:
            assert factors == 0
            assert len(expr.args) == n
        return True
    except AssertionError:
        return False
