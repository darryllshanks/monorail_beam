import pandas as pd
import math
from pathlib import Path
from eng_calcs.beam_design import SteelBeam
from eng_calcs.utils import str_to_float

MODULE_PATH = Path(__file__)
# print(f"{MODULE_PATH=}")
CWD = Path.cwd()
# print(f"{CWD=}")
DB_PATH = MODULE_PATH.parent
# print(f"{DB_PATH=}")


def import_sections_db() -> pd.DataFrame:
    """
    Returns a Pandas DataFrame of standard Australian I-Section sizes
    and geometric properties.
    """
    df = pd.read_csv(DB_PATH / "steel_section_sizes_AU.csv")
    df_cleaned = df.dropna()
    return df_cleaned


def sections_filter(sections_df: pd.DataFrame, operator: str, **kwargs) -> pd.DataFrame:
    """
    Returns a filtered Pandas DataFrame which contains only steel beam/column
    sections properties that suit the user input target values within a certain
    range (e.g. <= OR >=). The user may input more than one target value for 
    filtering.

    'sections_df': Pandas DataFrame containing steel beam/column data
    'operator': Accepts two filtering methods:
        ge: greater than or equal to
        le: less than or equal to
    '**kwargs': target value/s for filtering. The input parameters should match
    one or more of the column headings from the original DataFrame. Note that a
    partial 'Section' name may be used as a filter, and must be in a string
    format.
    """
    sub_df = sections_df.copy()
    for k, v in kwargs.items():
        if k == 'Designation':
            try:
                k_mask = sub_df[k].str.contains(v, case=False, na=False)
                sub_df = sub_df.loc[k_mask]
                if math.fsum(k_mask) == 0.0:
                    raise KeyError(f"The partial 'Designation' column name '{v}' is not within the data set!")
                else:
                    continue
            except TypeError:
                raise TypeError(f"The partial 'Section' column name '{v}' must be a string!")
        elif operator == 'ge':
            try:
                k_mask = sub_df[k] >= v
                sub_df = sub_df.loc[k_mask]
            except KeyError:
                raise KeyError(f"The column key '{k}' is not within the input DataFrame!")
        elif operator == 'le':
            try:
                k_mask = sub_df[k] <= v
                sub_df = sub_df.loc[k_mask]
            except KeyError:
                raise KeyError(f"The column key '{k}' is not within the input DataFrame!")
        else:
            raise ValueError(f"The operator parameter shall be either 'ge' or 'le', not {operator}!")

        # Checks if filtered DataFrame is empty
        if sub_df.empty:
            raise Exception(f"WARNING: No records match all of the parameters. Review applied filtering parameters.")
    return sub_df


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




# def create_solved_steelbeam_series(solved_sb: SteelBeam, dead_load: float, live_load: float) -> pd.Series:
#     """
#     Returns a Pandas Series using data from a solved 'SteelColumn' object in
#     the following format:
#         'Section Name'
#         'Height'
#         'Dead'
#         'Live'
#         'Factored Load'
#         'Axial Resistance'
#         'DCR (demand/capacity ratio)'
    
#     'sc': SteelColumn DataClass object
#     'dead_load': Unfactored dead load applied to the column
#     'live_load': Unfactored live load applied to the column
#     """
#     # Undertake the required calculations
#     loads = {'G_load': str_to_float(dead_load), 'Q_load': str_to_float(live_load)}
#     max_load = load_factors.max_factored_load(loads, load_factors.uls_load_combos())
#     capacity = sc.factored_compressive_resistance()
#     capacity_ratio = max_load / capacity

#     # Compile the SteelColumn dictionary
#     sc_dict = {
#         'Section Name': sc.tag,
#         'Height': sc.h,
#         'Dead': dead_load,
#         'Live': live_load,
#         'Factored Load': max_load,
#         # 'kf': sc.kf,
#         'Axial Resistance': capacity,
#         'DCR': capacity_ratio
#     }
#     sc_series = pd.Series(sc_dict)
#     return sc_series


# def create_sc_dataframe(
#         df: pd.DataFrame, 
#         col_height: float,
#         yield_stress: float,
#         kx: float,
#         ky: float,
#         dead_load: float,
#         live_load: float,
#         col_shape: str = 'Not Defined',
#         fab_method: str = 'HR',
#         e_mod: Optional[float] = 200000.0,
#         # tag: Optional[str] = 'Column 1',
#     ) -> pd.DataFrame:
#     """
#     Returns a DataFrame containing a series of solved 'SteelColumn' objects
#     in the following format.
#         'Section Name'
#         'Height'
#         'Dead'
#         'Live'
#         'Factored Load'
#         'Axial Resistance'
#         'DCR (demand/capacity ratio)'

#     Parameters:    
#     'df': Pandas DataFrame containing basic member geometric properties.
#     'col_height': Column height.
#     'yield_stress': Yield stress of the steel column.
#     'kx': Effective length factor about the x-axis.
#     'ky': Effective length factor about the y-axis.
#     'e_mod': Elastic Modulus for steel; default is 200000 MPa.
#     'tag': Optional column tag/name.
#     """
#     sub_df = df.copy().reset_index()

#     acc = []
#     for row in sub_df.index:
#         col_series = sub_df.iloc[row].squeeze()

#         sc = create_steelcolumn(
#             col_series, 
#             col_height=col_height,
#             yield_stress=yield_stress,
#             kx=kx,
#             ky=ky,
#             e_mod=e_mod,
#             col_shape=col_shape,
#             fab_method=fab_method
#         )
#         sc_series = create_sc_series(sc, dead_load=dead_load, live_load=live_load)
#         acc.append(sc_series)

#     sc_dataframe = pd.DataFrame(acc)

#     return sc_dataframe