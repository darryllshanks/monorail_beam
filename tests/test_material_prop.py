import math
import pytest
from .context import material_prop


def test_plate_yield_stress():
    t_1 = 10.0
    f_y_1 = '300'
    resi_stress_cat_1 = 'HR'
    assert math.isclose(material_prop.plate_yield_stress(f_y_1, t_1, resi_stress_cat_1), 320.0)

    t_2 = 10.0
    f_y_2 = '300'
    resi_stress_cat_2 = 'HW'
    assert math.isclose(material_prop.plate_yield_stress(f_y_2, t_2, resi_stress_cat_2), 310.0)


def test_plate_tensile_strength():
    f_y_1 = '300'
    resi_stress_cat_1 = 'HR'
    assert math.isclose(material_prop.plate_tensile_strength(f_y_1, resi_stress_cat_1), 440.0)

    f_y_2 = '250'
    resi_stress_cat_2 = 'HW'
    assert math.isclose(material_prop.plate_tensile_strength(f_y_2, resi_stress_cat_2), 410.0)