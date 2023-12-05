import pandas as pd
import math
from pathlib import Path
from monorail_beam.beam_design import SteelBeam
from monorail_beam.utils import str_to_float


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