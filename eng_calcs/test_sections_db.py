import pandas as pd
from eng_calcs import sections_db, beam_design


def test_import_sections_db():
    df_test = sections_db.import_sections_db()
    row_idx_0 = df_test.iloc[0]
    assert list(row_idx_0) == [
        '610 UB 125',
        'HR',
        125.0,
        611.6, 
        229.0, 
        19.6, 
        11.9, 
        14.0, 
        15957.0, 
        986302220.0, 
        3225318.0, 
        3679640.0, 
        249.0, 
        39324842.0, 
        343448.0, 
        535719.0, 
        49.6, 
        1561093.0,
        3.445490e+12
    ]


def test_sections_filter():
    test_df = pd.DataFrame(data = [
        ["UB", "UB_310", 40, 86.4],
        ["UB", "UB_530", 82, 477],
        ["UC", "UC_200", 46, 52.8],
        ["UC", "UC_250", 73, 114]],
        columns=["Type", "Section", "W", "Ix"]
    )
    filtered_df = sections_db.sections_filter(test_df, 'ge', Ix=100)

    assert filtered_df.iloc[0, 1] == 'UB_530'
    assert filtered_df.iloc[1, 1] == 'UC_250'


def test_create_steelbeam():
    df_test = sections_db.import_sections_db()
    section_size = '410 UB 53.7'
    steel_grade = '300'
    beam_name = 'Monorail Beam'
    section_series = sections_db.sections_filter(df_test, operator='ge', Designation=section_size).squeeze()
    test_beam = sections_db.create_steelbeam(section_series, steel_grade, beam_name)
    assert test_beam == beam_design.SteelBeam(
        A=6887.0, 
        I_x=187807278.0, 
        I_y=10264522.0, 
        Z_x=932972.0, 
        Z_y=115332.0, 
        S_x=1056546.0, 
        S_y=178889.0, 
        r_x=165.0, 
        r_y=38.6, 
        J=234294.0, 
        I_w=393719000000.0, 
        beam_tag='Monorail Beam', 
        d=402.6, 
        b_f=178.0, 
        t_f=10.9, 
        t_w=7.6, 
        r_1=11.4, 
        mass=53.7, 
        steel_grade='300', 
        phi=(0.9,), 
        resi_stress_cat='HR', 
        E=200000, 
        G=80000
    )