import pandas as pd
import math
from handcalcs.decorator import handcalc
from eng_calcs import beam_design, load_factors, sections_db, beam_analysis


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

def min_flg_thickness(
        N_W: float,
        f_y: float,
        f_b:float=0.0,
        K_L: float=1.3,
        C_F: float=1.0,
        B_F: float=1.0,
        n_cycles: float=1000
) -> float:
    """
    Returns the minimum flange thickness for a monorail beam per the
    equations provided in DR AS 1418:2023 Clause 5.12.3.1.
    """
    if n_cycles < 1000:
        T_F = K_L * ((2400 * C_F / B_F + 600) * N_W / (f_y - 1.1 * f_b)) ** 0.5
    elif n_cycles >= 1000:
        T_F = K_L * ((2400 * C_F / B_F + 600) * N_W / (0.67 * f_y - f_b)) ** 0.5
    return T_F


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
    phi_2 = load_factors.hoisted_load_dyn_factor(
        HC_class=hoisting_class,
        HD_class=hoist_drive_class, 
        v_hmax=max_steady_hoist_speed, 
        v_hcs=steady_hoist_creep_speed
    )
    print(f"phi_2 = {phi_2}")
    load_combos = load_factors.load_combos(phi_1=1.1, phi_2=phi_2)
    design_loads = load_factors.factored_load(input_loads, load_combos)
    return design_loads


def run_analysis(app_inputs: dict) -> dict:
    """
    
    """
    # Creates SteelBeam dataclass from user selected beam size, steel grade
    df_sections = sections_db.import_sections_db()
    section_size = app_inputs['Steel Data']['Section Size']
    steel_grade = app_inputs['Steel Data']['Steel Grade']
    beam_name = app_inputs['Project Details']['Beam Name']
    section_series = sections_db.sections_filter(df_sections, operator='ge', Designation=section_size).squeeze()
    sb_data = sections_db.create_steelbeam(section_series, steel_grade, beam_name)
    
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
    print(monorail_loads)

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

    return static_results, env_results, str_beam_data


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

    G_load_data = {}
    for lc_name in monorail_loads.keys():
        if lc_name == 'SLS':
            fact = 1.0
        elif lc_name == 'DLS':
            fact = 1.1
        elif lc_name == 'ULS':
            fact = 1.1 * 1.22
        loads = []
        for idx, segment in enumerate(app_inputs["Geometry"].items()):
            if segment[1]['Span'] == 0:
                continue
            else:
                loads.append([idx + 1, 1, fact * beam_mass, 0, 0])
        G_load_data.update({lc_name: loads})

    support_cond = []
    for support in spans:
        support_cond.append(-1)
        support_cond.append(0)
    if app_inputs["Cantilever"] == True:
        support_cond.append(0)
        support_cond.append(0)
    else:
        support_cond.append(-1)
        support_cond.append(0)
    
    structured_beam_data = {}
    structured_beam_data.update({'Name': beam_name})
    structured_beam_data.update({'L': spans})
    structured_beam_data.update({'EI': EI})
    structured_beam_data.update({'R': support_cond})
    structured_beam_data.update({'G_load':G_load_data})

    return structured_beam_data


