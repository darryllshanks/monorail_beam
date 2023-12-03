import math
import pytest
from .context import monorail_design


# Testing of nested dictionaries is not currently supported
# def test_load_combos():
#     phi_1 = 1.4
#     phi_2 = 1.5
#     load_combos = monorail_design.load_combos(phi_1, phi_2)
#     expected_result = {
#         "SLS": {"G": 1.0, "Q": 1.0},
#         "DLS": {"G": 1.4, "Q": 1.5},
#         "ULS": {"G": 1.708, "Q": 2.01}
#     }
#     assert load_combos == pytest.approx(expected_result)


def test_hoisted_load_dyn_factor():
    test_1 = monorail_design.hoisted_load_dyn_factor("HC1", "HD1", 0.25, 0.05)
    assert math.isclose(test_1, 1.0925, rel_tol=1e-4, abs_tol=1e-6)


def test_min_flg_thickness():
    test_1 = monorail_design.min_flg_thickness(
        N_W = 5,
        f_y = 300,
        f_b = 0.0,
        K_L = 1.0,
        C_F = 90.0,
        B_F = 100.0,
        n_cycles = 1000
    )
    assert math.isclose(test_1, 8.2859, rel_tol=1e-4, abs_tol=1e-6)
    test_2 = monorail_design.min_flg_thickness(
        N_W = 5,
        f_y = 300,
        f_b = 0.0,
        K_L = 1.3,
        C_F = 90.0,
        B_F = 100.0,
        n_cycles = 990
    )
    assert math.isclose(test_2, 8.817, rel_tol=1e-2, abs_tol=1e-6)


def test_min_web_thickness():
    test_1 = monorail_design.min_web_thickness(
        N_W = 5,
        f_y = 300,
        D = 300,
        C_F = 90.0,
        B_F = 100.0
    )
    assert math.isclose(test_1, 2.626, rel_tol=1e-2, abs_tol=1e-6)