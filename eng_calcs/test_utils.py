import math
from eng_calcs import utils


def test_str_to_int():
    test_str_1 = "43"
    test_str_2 = "-2000"
    test_str_3 = 'testint'

    assert utils.str_to_int(test_str_1) == 43
    assert utils.str_to_int(test_str_2) == -2000
    assert utils.str_to_int(test_str_3) == 'testint'


def test_str_to_float():
    test_str_1 = "43"
    test_str_2 = "-2000"
    test_str_3 = "324.625"
    test_str_4 = 'POINT:Fy'

    assert utils.str_to_float(test_str_1) == 43.0
    assert utils.str_to_float(test_str_2) == -2000.0
    assert utils.str_to_float(test_str_3) == 324.625
    assert utils.str_to_float(test_str_4) == 'POINT:Fy'


def test_round_down():
    test_1 = utils.round_down(decimals=1, n=3.142)
    assert math.isclose(test_1, 3.1, rel_tol=1e-6, abs_tol=1e-6)


def test_round_up():
    test_1 = utils.round_up(decimals=1, n=3.142)
    assert math.isclose(test_1, 3.2, rel_tol=1e-6, abs_tol=1e-6)