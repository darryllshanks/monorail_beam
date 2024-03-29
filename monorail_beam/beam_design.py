from typing import Optional
import pandas as pd
from dataclasses import dataclass
from math import pi, sqrt
from .material_prop import plate_yield_stress, plate_tensile_strength
from .utils import str_to_float


@dataclass
class Beam:
    """
    A data type to represent the geometric, plastic, and warping
    properties of a structural beam element.

    """
    A: float
    I_x: float
    I_y: float
    Z_x: float
    Z_y: float
    S_x: float
    S_y: float
    r_x: float
    r_y: float
    J: float
    I_w: float


@dataclass
class SteelBeam(Beam):
    """
    A data type to represent a steel I-Section beam with capacities
    calculated in accordance with AS 4100:2020(+A1).

    Attributes:
        beam_tag: a unique identifier representing the name of the beam
            on a drawing or in structural calculations.
        d: depth of section (mm)
        b_f: flange width (mm)
        t_f: flange thickness (mm)
        t_w: web thickness (mm)
        r_1: root radius (mm)
        steel_grade: the steel grade manufactured to Australian Standards.
        phi: the steel capacity reduction factor per AS 4100:2020(+A1).
        resi_stress_cat: the residual stress category
        E: modulus of elasticity (MPa)
        G: shear modulus of elasticity (MPa)

    """
    beam_tag: str
    d: float
    b_f: float
    t_f: float
    t_w: float
    r_1: float
    mass: float
    steel_grade: str
    phi: float=0.9,
    resi_stress_cat: str="HR"
    E: float=200000
    G: float=80000

    def yield_stress_flg(self):
        """
        Returns the flange yield stress in accordance with AS 4100:2020(+A1)
        Table 2.1 with respect to the steel grade, plate thickness, and 
        residual stress category.
        """
        f_yf = plate_yield_stress(
            self.steel_grade, 
            self.t_f,
            self.resi_stress_cat
        )
        return f_yf

    def yield_stress_web(self):
        """
        Returns the web yield stress in accordance with AS 4100:2020(+A1)
        Table 2.1 with respect to the steel grade, plate thickness, and 
        residual stress category.
        """
        f_yw = plate_yield_stress(
            self.steel_grade, 
            self.t_w,
            self.resi_stress_cat
        )
        return f_yw

    def tensile_strength(self):
        """
        Returns the section tensile strength in accordance with 
        AS 4100:2020(+A1) Table 2.1 with respect to the steel grade and 
        residual stress category.
        """
        f_u = plate_tensile_strength(
            self.steel_grade, 
            self.resi_stress_cat
        )
        return f_u

    def section_moment_capacity_x(self):
        """
        Returns the nominal section moment capacity for bending about
        the local x-axis (strong axis).

        """
        flg_outstand_width = (self.b_f - self.t_w) / 2
        web_clear_depth = (self.d - 2 * self.t_f)

        lamb_s, lamb_sy, lamb_sp = section_slenderness(
            flg_outstand_width,
            self.t_f,
            self.yield_stress_flg(),
            web_clear_depth,
            self.t_w,
            self.yield_stress_web(),
            self.resi_stress_cat,
            'x'
        )
        f_y = min(self.yield_stress_flg(), self.yield_stress_web())
        print(f"f_y = {f_y}")
        Z_ex = eff_section_modulus(self.S_x, self.Z_x, lamb_s, lamb_sy, lamb_sp)
        print(f"Z_ex = {Z_ex}")
        M_sx = section_moment_cap(Z_e=Z_ex, f_y=f_y)
        return M_sx
    
    def section_moment_capacity_y(self):
        """
        Returns the nominal section moment capacity for bending about
        the local y-axis (weak axis).

        """
        flg_outstand_width = (self.b_f - self.t_w) / 2
        web_clear_depth = (self.d - 2 * self.t_f)

        print(f"Flange Outstand Width {flg_outstand_width}")
        print(f"Web Clear Depth {web_clear_depth}")

        lamb_s, lamb_sy, lamb_sp = section_slenderness(
            flg_outstand_width,
            self.t_f,
            self.yield_stress_flg(),
            web_clear_depth,
            self.t_w,
            self.yield_stress_web(),
            self.resi_stress_cat,
            'y'
        )

        f_y = min(self.yield_stress_flg(), self.yield_stress_web())
        Z_ey = eff_section_modulus(self.S_y, self.Z_y, lamb_s, lamb_sy, lamb_sp)
        print(f"Z_ey = {Z_ey}")
        M_sy = section_moment_cap(Z_e=Z_ey, f_y=f_y)
        return M_sy


def element_slenderness(b: float, t:float, f_y: float) -> float:
    """
    Calculates the slenderness of a compression plate element in an I-Section
    member in accordance with AS 4100:2020(+A1) Clause 5.2.2.

    Args:
        b: Clear width of the element outstand from the face of the supporting
            plate element OR the clear width of the element between the faces 
            of supporting plate elements.
        t: Element thickness.
        f_y: Plate element yield stress (MPa).

    Returns:
        Slenderness of a compression plate element.

    """
    lamb_e = b / t * (f_y / 250) ** 0.5
    print(f"lambda_e = {lamb_e}")
    return lamb_e


def section_slenderness(
        flg_outstand_width: float,
        flg_thickness: float,
        flg_yield: float,
        web_clear_depth: float,
        web_thickness: float,
        web_yield: float,
        resi_stress_cat: Optional[str]="HR",
        axis: Optional[str]="x"
    ) -> tuple[float, float, float]:
    """
    Calculates the section slenderness lambda parameters of an I-Section beam,
    calculated in accordance with AS 4100:2020(+A1) Clause 5.2.2.

    Args:
        flange_outstand_width: Clear width of flange outstand from face of 
            supporting plate/s
        flange_thickness: Flange thickness.
        flange_yield: Flange yield stress.
        web_clear_depth: Clear depth of web between flanges.
        web_thickness: Flange thickness.
        web_yield: Web yield stress.
        resi_stress_cat: Residual stress category of either 'HR', 'HW', or 'LW'.

    Returns:
        tuple(lamb_s, lamb_sy, lamb_sp)
    
    """
    try:
        if resi_stress_cat == "HR":
            if axis == "x":
                lamb_ey_flg = 16
                lamb_ep_flg = 9
                lamb_ey_web = 115
                lamb_ep_web = 82
            elif axis == "y":
                lamb_ey_flg = 25
                lamb_ep_flg = 9
        elif resi_stress_cat == "HW":
            if axis == "x":
                lamb_ey_flg = 14
                lamb_ep_flg = 8
                lamb_ey_web = 115
                lamb_ep_web = 82
            elif axis == "y":
                lamb_ey_flg = 22
                lamb_ep_flg = 8
        elif resi_stress_cat == "LW":
            if axis == "x":
                lamb_ey_flg = 15
                lamb_ep_flg = 8
                lamb_ey_web = 115
                lamb_ep_web = 82
            elif axis == "y":
                lamb_ey_flg = 22
                lamb_ep_flg = 8
    except:
        raise KeyError(f"The residual stress classification shall be either 'HR', 'LW, or 'HW', not {resi_stress_cat}")

    lamb_e_flg = element_slenderness(flg_outstand_width, flg_thickness, flg_yield)
    flg_ratio = lamb_e_flg / lamb_ey_flg
    print(f"Flange lambda_e Ratio = {flg_ratio}")

    if axis == 'x':
        lamb_e_web = element_slenderness(web_clear_depth, web_thickness, web_yield)
        web_ratio = lamb_e_web / lamb_ey_web 
        print(f"Web lambda_e Ratio = {web_ratio}")
        if flg_ratio >= web_ratio:
            lamb_s = lamb_e_flg
            lamb_sy = lamb_ey_flg
            lamb_sp = lamb_ep_flg
        else:
            lamb_s = lamb_e_web
            lamb_sy = lamb_ey_web
            lamb_sp = lamb_ep_web
    elif axis == 'y':
        lamb_s = lamb_e_flg
        lamb_sy = lamb_ey_flg
        lamb_sp = lamb_ep_flg

    return lamb_s, lamb_sy, lamb_sp


def eff_section_modulus(S: float, Z: float, lamb_s: float, lamb_sy: float, lamb_sp: float) -> float:
    """
    Calculates the effective section modulus of an I-Section in accordance with
    AS 4100:2020(+A1) Clause 5.2.3 to 5.2.5.

    Args:
        S: Plastic section modulus.
        Z: Elastic section modulus.
        lamb_s: Section slenderness.
        lamb_sy: Section yield slenderness limit.
        lamb_sp: Section plasticity slenderness limit.

    Returns:
        float

    """
    print(f"lambda_s = {lamb_s}, lambda_sp = {lamb_sp}, lambda_sy = {lamb_sy}")
    if lamb_s <= lamb_sp:
        Z_e = min(S, 1.5 * Z)
    elif lamb_s <= lamb_sy:
        Z_c = min(S, 1.5 * Z)
        Z_e = Z + (lamb_sy - lamb_s) / (lamb_sy - lamb_sp) * (Z_c - Z)
    else:
        Z_e = Z * (lamb_sy / lamb_s)
    return Z_e


def section_moment_cap(Z_e: float, f_y: float, phi: float=0.9) -> float:
    """
    Calculates the factored nominal section moment capacity of a steel member,
    calculated in accordance with AS 4100:2020(+A1) Clause 5.2.1.

    Args:
        Z_e: Effective section modulus.
        f_y: Yield stress of steel material.
        phi: Material resistance factor (the default=0.9).

    Returns:
        Factored section moment capacity.

    Notes:
      * Uniaxial bending about a principal axis.
      * This function does not assume units. The user is responsible for
        ensuring that consistent units are being used for the results to be
        valid.

    """
    M_s = phi * Z_e * f_y
    return M_s


def bending_eff_length(
        l_seg: float, 
        d_1: float, 
        t_f: float, 
        t_w: float, 
        n_w: float=1.0,
        rest_arrg: str='FF',
        load_height: bool=True,
        pos_of_load: bool=True,
        lat_rot_restraint: str="None"
) -> float:
    """
    Calculates the effective length of a segment or sub-segment of a steel
    member, subject to bending moments about the major principal x-axis. The k
    modification factors are determined in accordance with AS 4100:2020(+A1) 
    Clause 5.6.3.

    Args:
        l_seg: Length of the beam segment or sub-segment.
        d_1: Clear depth between flanges, ignoring fillets or welds.
        t_f: Thickness of critical flange.
        t_w: Thickness of web.
        n_w: Number of webs.
        rest_arrg: The restraint arrangement of the beam segment/sub-segment
            that matches the restraint conditions at both ends of the beam. The
            input shall be one of the following: 
            {'FF', 'FP', 'FL', 'PP', 'PL', 'LL', 'FU', 'PU'} (the default is 
            'FF').
        load_height: Load height position of the applied load (the default is 
            True, equivalent to a load height position of 'Top Flange'. False 
            is equivalent to a load height position of 'Shear Centre').
        pos_of_load: Longitudinal position of the load, (the default is True,
            equivalent to a load position as 'Within Segment'. False is
            equivalent to a load position to 'At Segment End').
        lat_rot_restraint: Defines the ends of a beam with lateral rotational 
            restraints of either {'None', 'One', 'Both', 'Any'}, (the default 
            is 'None').

    Returns:
        Effective length of a steel beam segment or sub-segment.

    """
    # Determines the twist restraint factor k_t
    if rest_arrg == "FP" or rest_arrg == "PL" or rest_arrg == "PU":
        k_t = 1 + ((d_1 / l_seg) * (t_f / (2 * t_w)) ** 3 ) / n_w
    elif rest_arrg == "PP":
        k_t = 1 + (2 * (d_1 / l_seg) * (t_f / (2 * t_w)) ** 3 ) / n_w
    else: k_t = 1

    # Determines the load height factor k_l
    if load_height == True:
        if rest_arrg == "FU" or rest_arrg == "PU": k_l = 2.0
        elif pos_of_load == True: k_l = 1.4
        else: k_l = 1.0
    else: k_l = 1.0

    # Determines the lateral rotation restraint factor k_r
    if rest_arrg == "FF" or rest_arrg == "FP" or rest_arrg == "PP":
        if lat_rot_restraint == "One": k_r = 0.85
        elif lat_rot_restraint == "Two": k_r = 0.70
        else: k_r = 1.0
    else: k_r = 1.0

    l_e = k_t * k_l * k_r * l_seg
    return l_e


def moment_mod_factor(M_m: float, M_2: float, M_3: float, M_4: float)-> float:
    """
    Calculates the moment modification factor 'alpha_m' calculated in accordance 
    with AS4100:2020(+A1) Clause 5.6.1.1 (iii).

    Args:
        M_m: Maximum deisng bending moment in the segment.
        M_2 and M_4: Design bending moments at the quarter points of the segment
        M_3: Design bending moment at the midpoint of the segment.

    Returns:
        Moment modification factor

    """
    alpha_m = min(1.7 * M_m / (M_2 ** 2 + M_3 **2 + M_4 **2), 2.5)
    return alpha_m


def member_moment_cap(M_sx: float, l_e: float, I_y: float, I_w: float, J: float, E: float, G: float, alpha_m: float=1.0, phi: float=0.9):
    """
    Calculates the factored nominal member moment capacity of a steel member,
    calculated in accordance with AS4100:2020(+A1) Clause 5.6.1.1.

    Args:
        M_sx: Nominal section moment capacity about the major principal x-axis.
        l_e: Bending effective length for the segment under consideration.
        I_y: Second moment of area about the minor principal y-axis.
        I_w: Warping constant.
        J: Torsion constant.
        E: Modulus of elasticity.
        G: Shear modulus of elasticity.
        alpha_m: Moment modification factor (the default=1.0).
        phi: Material resistance factor (the default=0.9).

    Returns:
        Factored member moment capacity.

    Notes:
      * It is assumed that the input nominal section moment capacity has not 
        been factored by any material resistance factors.
      * This function does not assume units. The user is responsible for
        ensuring that consistent units are being used for the results to be
        valid.
    """
    M_o = sqrt(((pi ** 2 * E * I_y) / l_e ** 2) * (G * J + ((pi ** 2 * E * I_w) / l_e ** 2)))
    alpha_s = 0.6 * (sqrt((M_sx / M_o) ** 2 + 3) - M_sx / M_o)
    M_bx = phi * alpha_m * alpha_s * M_sx
    return M_bx


def create_steelbeam(
        beam_prop: pd.Series,
        steel_grade: str,
        beam_tag: str
) -> SteelBeam:
    """
    Returns a Steel_I_Beam dataclass, populated with the data stored in
    a Pandas series 'beam_prop'.
    """
    pd.to_numeric(beam_prop, 'ignore')
    sb = SteelBeam(
        A=str_to_float(beam_prop['A']),
        I_x=str_to_float(beam_prop['Ix']),
        I_y=str_to_float(beam_prop['Iy']),
        Z_x=str_to_float(beam_prop['Zx']),
        Z_y=str_to_float(beam_prop['Zy']),
        S_x=str_to_float(beam_prop['Sx']),
        S_y=str_to_float(beam_prop['Sy']),
        r_x=str_to_float(beam_prop['rx']),
        r_y=str_to_float(beam_prop['ry']),
        J=str_to_float(beam_prop['J']),
        I_w=str_to_float(beam_prop['Iw']),
        beam_tag=beam_tag,
        d=str_to_float(beam_prop['d']),
        b_f=str_to_float(beam_prop['bf']),
        t_f=str_to_float(beam_prop['tf']),
        t_w=str_to_float(beam_prop['tw']),
        r_1=str_to_float(beam_prop['r1']),
        mass=str_to_float(beam_prop['Mass']),
        steel_grade=steel_grade,
        resi_stress_cat=beam_prop['Class']
    )
    return sb


