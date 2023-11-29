import math
import pytest
from eng_calcs import beam_design

def test_element_slenderness():
    b_1 = 300.0
    t_1 = 10.0
    f_y_1 = 320
    assert math.isclose(beam_design.element_slenderness(b_1, t_1, f_y_1), 33.941, rel_tol=1e-4, abs_tol=1e-6)


def test_section_slenderness():
    lamb_s1, lamb_sy1, lamb_sp1 = beam_design.section_slenderness(
        flg_outstand_width = 144.0,
        flg_thickness = 20.0,
        flg_yield = 300.0,
        web_clear_depth = 860.0,
        web_thickness = 12.0,
        web_yield = 310.0,
        resi_stress_cat = "HR",
        axis = "x"
    )
    assert math.isclose(lamb_s1, 79.8046, rel_tol=1e-5, abs_tol=1e-6)
    assert math.isclose(lamb_sy1, 115, rel_tol=1e-5, abs_tol=1e-6)
    assert math.isclose(lamb_sp1, 82, rel_tol=1e-5, abs_tol=1e-6)


def test_eff_section_modulus():
    Z_e1 = beam_design.eff_section_modulus(
        S = 7498800,
        Z = 6577013,
        lamb_s = 79.8046,
        lamb_sy = 115,
        lamb_sp = 82
    )
    assert math.isclose(Z_e1, 7498800, rel_tol=1e-5, abs_tol=1e-6)


def test_section_moment_cap():
    test_data_1 = beam_design.section_moment_cap(
        Z_e = 7498800,
        f_y = 300.0,
        phi = 0.9
    )
    assert math.isclose(test_data_1, 2024676000, rel_tol=1e-5, abs_tol=1e-6)


def test_bending_eff_length():
    test_data_1 = beam_design.bending_eff_length(
        l_seg = 4000, 
        restraint_arrg = "FF", 
        d_1 = 333.0, 
        t_f = 9.7, 
        t_w = 6.9, 
        n_w = 1,
        load_height ="Top Flange",
        pos_of_load ="Within Segment",
        lat_rot_restraint ="One"
    )
    assert math.isclose(test_data_1, 4760, rel_tol=1e-5, abs_tol=1e-6)

    test_data_2 = beam_design.bending_eff_length(
        l_seg = 4000, 
        restraint_arrg = "FU", 
        d_1 = 333.0, 
        t_f = 9.7, 
        t_w = 6.9, 
        n_w = 1,
        load_height ="Top Flange",
        pos_of_load ="Within Segment",
        lat_rot_restraint ="One"
    )
    assert math.isclose(test_data_2, 8000, rel_tol=1e-5, abs_tol=1e-6)


def test_member_moment_cap():
    test_1 = beam_design.member_moment_cap(
        M_sx = 337777777.8,
        l_e = 4000.0,
        I_y = 10264522,
        I_w = 393718554210,
        J = 234294,
        E = 200000,
        G = 80000,
        alpha_m = 1.0,
        phi = 0.9
    )
    assert math.isclose(test_1, 168900000, rel_tol=1e-5, abs_tol=1e-6)