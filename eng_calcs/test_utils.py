import utils


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