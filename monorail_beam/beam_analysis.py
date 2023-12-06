import math
import pycba as cba
import numpy as np
from monorail_beam import utils


def find_load_pos_for_PyCBA(load_pos: float, spans: list) -> int:
    """
    Returns the span index of a load position that is provided with
    respect to the total continuous beam length.

    Args:
        load_pos: 'x' distance of the applied point load on the beam.
        spans: List containing the length of each span between supports.

    Returns:
        Span index

    """
    list_len = len(spans)
    rnd_load_pos = utils.round_down(load_pos, 4)
    for idx, seg in enumerate(spans):
        if idx == 0:
            if (seg - rnd_load_pos) >= 0:
                span_idx = 1
                break
            else:
                cum_sum = seg
                continue
        elif idx == (list_len - 1):
            span_idx = list_len
            break
        else:
            if (seg + cum_sum - rnd_load_pos) >= 0:
                span_idx = 1 + idx
                print(f"idx {idx}")
                break
            else:
                cum_sum = seg + cum_sum
    return span_idx

def static_beam_model(beam_model_data: dict, G_load: float, Q_load: float, Q_load_pos: float, n_points: int=1000) -> list:
    """
    Returns a dictionary of matrixes and critical values from a static
    analysis of a continuous beam element solved in PyCBA.

    Args:
        beam_model_data: A dict containing the relevant information required
            by PyCBA to build an analysis model.
        G_load: Dead load (kN)
        Q_load: Live load (kN)
        Q_load_pos: 'x' distance of the applied point load on the beam.
        n_points: The number of evaluation points along a member for load 
            effects.

    Returns:
        A dict of matrixes and critical values results. For example:
        {
            "Matrixes": {
                "Deflections": np.array,
                "Moment": np.array,
                "Shear": np.array,
                "x_dist": np.array
            },
            "Critical Values": {
                "Deflections": [D_max, D_min],
                "Moment": [M_max, M_min],
                "Shear": [V_max, V_min],
                "Reactions": [Reactions]
            }
        }

    """
    # Creates BeamAnalysis model
    L = beam_model_data['L']
    EI = beam_model_data['EI']
    R = beam_model_data['R']

    # Determines the load position index to be compatible with PyCBA
    span_idx = find_load_pos_for_PyCBA(Q_load_pos, L)
    a_dist = Q_load_pos - sum(L[:(span_idx - 1)])

    # Applies loads and runs the analysis
    LM_G = G_load
    LM_Q = [[span_idx,2,Q_load,a_dist,0]]
    LM_C = LM_G + LM_Q
    beam_model = cba.BeamAnalysis(L, EI, R, LM_C)
    beam_model.analyze(n_points)

    # Extracts results matrixes, min and max values, and stores into a dictionary.
    D_max = beam_model.beam_results.results.D.max() * 1000 # Converts to mm
    D_min = beam_model.beam_results.results.D.min() * 1000 # Converts to mm
    M_max = beam_model.beam_results.results.M.max() # kNm
    M_min = beam_model.beam_results.results.M.min() # kNm
    V_max = beam_model.beam_results.results.V.max() # kN
    V_min = beam_model.beam_results.results.V.min() # kN

    # Generates the results output dictionary
    results_output = {}
    results_output.update(
        {
            "Matrixes": {
                "Deflections": beam_model.beam_results.results.D,
                "Moment": beam_model.beam_results.results.M,
                "Shear": beam_model.beam_results.results.V,
                "x_dist": beam_model.beam_results.results.x
            },
            "Critical Values": {
                "Deflections": [D_max, D_min],
                "Moment": [M_max, M_min],
                "Shear": [V_max, V_min],
                "Reactions": beam_model.beam_results.R
            }
        }
    )
    return results_output  


def env_beam_model(beam_model_data: dict, G_load: float, Q_load: float, n_points: int=1000) -> list:
    """
    Returns a dictionary of matrixes and critical values from an enveloped
    moving load analysis for a continuous beam element solved in PyCBA.

    Args:
        beam_model_data: A dict containing the relevant information required
            by PyCBA to build an analysis model.
        G_load: Dead load (kN)
        Q_load: Live load (kN)
        n_points: The number of evaluation points along a member for load 
            effects.

    Returns:
        A dict of matrixes and critical values results. For example:
        {
            "Matrixes": {
                "Mmax": np.array,
                "Mmin": np.array,
                "Vmax": np.array,
                "Vmin": np.array,
                "x_dist": np.array
            },
            "Critical Values": {

            }
        }

    """
    # Creates BeamAnalysis model
    L = beam_model_data['L']
    EI = beam_model_data['EI']
    R = beam_model_data['R']
    LM_G = G_load
    beam_model = cba.BeamAnalysis(L, EI, R, LM_G)
    beam_model.analyze(n_points)

    # Adjusts the load incrementing if the cantilever length is less than 100mm
    if L[-1] <= 0.1:
        inc = 0.01
    else:
        inc = 0.05

    load_spacing = [] # Empty list for hoist loads
    axle_loads = [Q_load]
    moving_hoist_load = cba.Vehicle(axle_spacings=load_spacing, axle_weights=axle_loads)
    bridge_model = cba.BridgeAnalysis(beam_model, moving_hoist_load)
    results_env = bridge_model.run_vehicle(inc, plot_env=False, plot_all=False)

    # Generates the results output dictionary
    results_output = {}
    results_output.update(
        {
            "Matrixes": {
                "Mmax": results_env.Mmax,
                "Mmin": results_env.Mmin,
                "Vmax": results_env.Vmax,
                "Vmin": results_env.Vmin,
                "x_dist": results_env.x
            },
            "Critical Values": bridge_model.critical_values(results_env)
        }
    )
    return results_output    