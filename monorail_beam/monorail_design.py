

HOISTING_CLASS_FACTORS = {
    "HC1": 0.17,
    "HC2": 0.34,
    "HC3": 0.51,
    "HC4": 0.68
}

PHI_2_MIN = {
    "HC1": {"HD1": 1.05, "HD2": 1.05, "HD3": 1.05, "HD4": 1.05, "HD5": 1.05},
    "HC2": {"HD1": 1.10, "HD2": 1.10, "HD3": 1.05, "HD4": 1.10, "HD5": 1.05},
    "HC3": {"HD1": 1.15, "HD2": 1.15, "HD3": 1.05, "HD4": 1.15, "HD5": 1.05},
    "HC4": {"HD1": 1.20, "HD2": 1.20, "HD3": 1.05, "HD4": 1.20, "HD5": 1.05}
}

CHAR_HOIST_SPEED = {
    "HD1": {"A1": "v_hmax", "C1": "v_hmax"},
    "HD2": {"A1": "v_hcs", "C1": "v_hmax"},
    "HD3": {"A1": "v_hcs", "C1": "v_hmax"},
    "HD4": {"A1": "v_hcs", "C1": "v_hmax"},
}


def hoisted_load_dyn_factor(HC_class: float, HD_class: float, v_hmax: float, v_hcs: float) -> float:
    """
    Calculates the hoisted load dynamic factor in accordance with
    AS 5221.1:2021 Clause 6.1.2.1.

    'HC_class': the hoisting class per AS 5221.1:2021 Table 2a
    'HD_class': the hoist drive class per AS 5221.1:2021 Clause 6.1.2.1.3.
    'v_hmax': the maximum stead hoisting speed of the main hoist for load
        combinations A1 and B1.
    'v_hcs': the steady hoisting creep speed.
    """
    beta_2 = HOISTING_CLASS_FACTORS[HC_class]
    phi_2_min = PHI_2_MIN[HC_class][HD_class]

    if HD_class == "HD1":
        v_h = v_hmax
    elif HD_class == "HD2" or HD_class == "HD3":
        v_h = v_hcs
    elif HD_class == "HD4":
        v_h = 0.5 * v_hmax
    else: v_h = 0.0

    phi_2 = phi_2_min + beta_2 * v_h
    return phi_2


def load_combos(phi_1: float=1.1, phi_2: float=1.43) -> dict:
    """
    Returns a dictionary containing the monorail dead and live load
    factors, keyed with the load cases 'SLS' (Serviceability Limit State),
    'DLS' (Dynamic Limit State), and 'ULS' (Ultimate Limit State).

    If no arguments are provided, a hoisted load dynamic factor of 
    1.43 is adopted. This is calculated using a maximum lifting speed of
    20 m/min and the maximum value of phi_2,min from AS 5221.1:2021 
    Table 2a.
    """
    load_combos = {
        "SLS": {"G": 1.0, "Q": 1.0},
        "DLS": {"G": 1.0 * phi_1, "Q": 1.0 * phi_2},
        "ULS": {"G": 1.22 * phi_1, "Q": 1.34 * phi_2}
    }
    return load_combos


def factor_load(
        G_load: float=0.0, G: float=0.0, 
        Q_load: float=0.0, Q: float=0.0,
    ) -> float:
    """
    Returns the factored load based on individual input loads and 
    corresponding factors.

    'xx_load' - Load for particular load case i.e. 'G_load' - Dead Load
    'xx' - Corresponding load case factor i.e. 'G' - Dead Load Factor
    """
    factored_load = G_load * G + Q_load * Q
    return factored_load


def factored_load(loads: dict, load_combos: dict) -> dict:
    """
    Returns the maximum factored load based on the parameters stored in
    the dictionaries 'loads' and 'load_combos'.
    """
    factored_loads = {}
    # print(loads)
    # print(load_combos)
    for lc_name, lc_val in load_combos.items():
        factored_load = factor_load(**loads, **lc_val)
        factored_loads.update({lc_name: factored_load})
    return factored_loads


def min_flg_thickness(
        N_W: float,
        f_y: float,
        C_F: float,
        B_F: float,
        f_b:float=0.0,
        K_L: float=1.3,
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


def min_web_thickness(
        N_W: float,
        f_y: float,
        D: float,
        C_F: float=1.0,
        B_F: float=1.0
) -> float:
    """
    Returns the minimum web thickness for a monorail beam per the
    equations provided in DR AS 1418:2023 Clause 5.12.3.1.
    """
    T_W = ((240 * C_F / B_F + 60) * D / (2 * B_F) * N_W / f_y) ** 0.5
    return T_W