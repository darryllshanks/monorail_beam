import pandas as pd
import math
from pathlib import Path
from handcalcs.decorator import handcalc
from monorail_beam import beam_design, monorail_design, sections_db, beam_analysis


def section_list(beam_type: str):
    """
    Create a dynamic drop-down list for available section sizes based
    on the user selection for the residual stress category.
    """
    df_sections = sections_db.import_sections_db()
    # mask = df_sections['Designation'] == beam_type
    filt_df = sections_db.sections_filter(df_sections, operator='ge', Designation=beam_type)
    section_list = list(filt_df['Designation'])
    return section_list


def calc_min_element_thickness(
        N_W: float,
        f_y: float,
        C_F: float,
        B_F: float,
        D: float,
        f_b:float=0.0,
        K_L: float=1.3,
        n_cycles: float=1000
) -> float:
    """
    Returns the minimum web and flange thicknesses as determined
    from DR AS 1418:2023.
    """
    T_F = monorail_design.min_flg_thickness(N_W, f_y, C_F, B_F, f_b, K_L, n_cycles)
    T_W = monorail_design.min_web_thickness(N_W, f_y, D, C_F, B_F)
    return T_F, T_W

def monorail_design_loads(
        input_loads: dict,
        hoist_drive_class: str, 
        hoisting_class: str, 
        max_steady_hoist_speed: float,
        steady_hoist_creep_speed: float
) -> dict:
    """
    Returns a dictionary containing the factored monorail dead and live
    load, keyed with the load cases 'SLS' (Serviceability Limit State),
    'DLS' (Dynamic Limit State), and 'ULS' (Ultimate Limit State).
    """
    phi_2 = monorail_design.hoisted_load_dyn_factor(
        HC_class=hoisting_class,
        HD_class=hoist_drive_class, 
        v_hmax=max_steady_hoist_speed, 
        v_hcs=steady_hoist_creep_speed
    )
    print(f"phi_2 = {phi_2}")
    load_combos = monorail_design.load_combos(phi_1=1.1, phi_2=phi_2)
    design_loads = monorail_design.factored_load(input_loads, load_combos)
    return design_loads


def run_analysis(app_inputs: dict) -> dict:
    """
    Returns two separate dictionaries containing beam analysis results
    from PyCBA based on user provided inputs from the monorail_beam_app.

    The static_results dictionary is keyed in the following format:
        {
            "Matrixes": {
                "Deflections": ,
                "Moment": ,
                "Shear": ,
                "x_dist": 
            },
            "Critical Values": {
                "Deflections": ,
                "Moment": ,
                "Shear": ,
                "Reactions": 
            }
        }

    The env_results dictionary is keyed in the following format:
        {
            "Matrixes": {
                "Mmax": ,
                "Mmin": ,
                "Vmax": ,
                "Vmin": ,
                "x_dist": 
            },
            "Critical Values": 
        }
    """
    # Creates SteelBeam dataclass from user selected beam size, steel grade
    df_sections = sections_db.import_sections_db()
    section_size = app_inputs['Steel Data']['Section Size']
    steel_grade = app_inputs['Steel Data']['Steel Grade']
    beam_name = app_inputs['Project Details']['Beam Name']
    section_series = sections_db.sections_filter(df_sections, operator='ge', Designation=section_size).squeeze()
    sb_data = beam_design.create_steelbeam(section_series, steel_grade, beam_name)
     
    # Extracts the load data and creates a dictionary of factored monorail loads
    input_loads = app_inputs['Loads']
    hoist_drive_class = app_inputs['Hoist Data']['HD_Class']
    hoisting_class = app_inputs['Hoist Data']['HC_Class']
    max_steady_hoist_speed = app_inputs['Hoist Data']['Max Steady Hoist Speed']
    steady_hoist_creep_speed = app_inputs['Hoist Data']['Steady Hoist Creep Speed']
    Q_load_pos = app_inputs['Load Position'] * 1e-3

    monorail_loads = monorail_design_loads(
        input_loads,
        hoist_drive_class,
        hoisting_class,
        max_steady_hoist_speed,
        steady_hoist_creep_speed
    )
    print(f"Factored Monorail Loads {monorail_loads}")

    sb_data.Q_load_sls = monorail_loads['SLS']
    sb_data.Q_load_dls = monorail_loads['DLS']
    sb_data.Q_load_uls = monorail_loads['ULS']
    sb_data.size = section_size

    # Creates structured data to be used in PyCBA
    str_beam_data = create_PyCBA_data(sb_data, app_inputs, monorail_loads)

    # Creates a static load matrix for the hoist in a specified location
    static_results = {}
    for lc_name, Q_load in monorail_loads.items():
        G_load = str_beam_data['G_load'][lc_name]
        static_acc = beam_analysis.static_beam_model(str_beam_data, G_load, Q_load, Q_load_pos)
        static_results.update({lc_name: static_acc})

    # Creates the enveloped load matrixes
    env_results = {}
    for lc_name, Q_load in monorail_loads.items():
        G_load = str_beam_data['G_load'][lc_name]
        env_acc = beam_analysis.env_beam_model(str_beam_data, G_load, Q_load)
        env_results.update({lc_name: env_acc})
    return static_results, env_results, sb_data


def create_PyCBA_data(sb_data: beam_design.SteelBeam, app_inputs: dict, monorail_loads: dict) -> dict:
    """
    Returns a dictionary for an input list of beam data.
    """
    beam_name = sb_data.beam_tag
    beam_mass = sb_data.mass * 9.81e-3
    EI = sb_data.I_x * sb_data.E * 1e-9

    spans = []
    for idx, segment in enumerate(app_inputs["Geometry"].items()):
        if segment[1]['Span'] == 0:
            continue
        else:
            spans.append(segment[1]['Span'] / 1000)
    print(f"Spans: {spans}")
    if len(spans) == 0:
        raise ValueError(f"No beam spans have been entered!")

    G_load_data = {}
    for lc_name in monorail_loads.keys():
        if lc_name == 'SLS':
            fact = 1.0
        elif lc_name == 'DLS':
            fact = 1.1
        elif lc_name == 'ULS':
            fact = 1.1 * 1.22
        loads = []
        count = 0
        acc = []
        for segment in app_inputs["Geometry"].items():
            if segment[1]['Span'] == 0:
                continue
            else:
                acc.append(1)
            loads.append([len(acc), 1, fact * beam_mass, 0, 0])
        G_load_data.update({lc_name: loads})

    support_cond = []
    for span in spans:
        # Sets restraints to node on LHS of beam
        if span != 0:
            support_cond.append(-1)
            support_cond.append(0)
        else:
            continue

    if len(spans) == 1:
        support_cond.append(-1)
        support_cond.append(0)
    elif len(spans) == 2:
        if app_inputs["Cantilever"] == True:
            support_cond.append(0)
            support_cond.append(0)
        else:
            support_cond.append(-1)
            support_cond.append(0)
    elif len(spans) == 3:
            support_cond.append(0)
            support_cond.append(0)

    print(f"Support Cond {support_cond}")

    structured_beam_data = {}
    structured_beam_data.update({'Name': beam_name})
    structured_beam_data.update({'L': spans})
    structured_beam_data.update({'EI': EI})
    structured_beam_data.update({'R': support_cond})
    structured_beam_data.update({'G_load':G_load_data})

    return structured_beam_data


def beam_capacity(app_inputs: dict, sb: sections_db.SteelBeam) -> dict:
    """
    Returns a dict with the results of the primary beam capacity checks
    undertaken in accordance with AS 4100:2020(+A1).
    """
    capacity_results = sb.A

    sect_moment_cap = sb.section_moment_capacity_x()
    unfact_sect_moment_cap = sect_moment_cap / 0.9
    print(sect_moment_cap)

    capacity_results = {}
    capacity_results.update({"M_sx": sect_moment_cap})

    for span, values in app_inputs["Geometry"].items():
        length = app_inputs['Geometry'][span]['Span']
        restraint = app_inputs['Geometry'][span]['Restraint']
        if length != 0:
            l_e = beam_design.bending_eff_length(
                l_seg=length,
                restraint_arrg=restraint,
                d_1=sb.d - 2 * sb.t_f,
                t_f=sb.t_f,
                t_w=sb.t_w,
                n_w=1.0,
                load_height='Shear Centre',
                pos_of_load="Within Segment",
                lat_rot_restraint="None"
            )
            alpha_m = 1.0
            memb_moment_cap = beam_design.member_moment_cap(
                M_sx=unfact_sect_moment_cap, 
                l_e=l_e, 
                I_y=sb.I_y, 
                I_w=sb.I_w, 
                J=sb.J, 
                E=sb.E, 
                G=sb.G, 
                alpha_m=alpha_m,
                phi=0.9
            )
            capacity_results.update({span: {"l_e": l_e, "alpha_m": alpha_m, "M_bx": memb_moment_cap}})
        else:
            continue

    return capacity_results