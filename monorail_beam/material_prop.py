

def plate_yield_stress(steel_grade: str, t: float, resi_stress_cat) -> float:
    """
    Returns the steel plate element yield stress 'fy' based on the
    input 'steel grade' and plate thickness.

    steel_grade: Steel grade in accordance with AS/NZS 3678 or AS/NZS 3679.1.
    t: Plate thickness (mm)
    resi_stress_cat: Residual Stress Category for the plate. Used to
        determine categorise the steel element in accordance with
        AS 4100:2020(+A1) Table 2.1.
    """
    if resi_stress_cat == "HR":
        if steel_grade == '250':
            if t <= 12.0:
                f_y = 260.0
            elif t < 40.0:
                f_y = 250.0
            else:
                f_y = 230.0
            f_u_plate = 410.0
        elif steel_grade == '300':
            if t < 11.0:
                f_y = 320.0
            elif t <= 17.0:
                f_y = 300.0
            else:
                f_y = 280.0
            f_u_plate = 440.0
        elif steel_grade == '350':
            if t <= 11.0:
                f_y = 360.0
            elif t < 40.0:
                f_y = 340.0
            else:
                f_y = 330.0
            f_u_plate = 480.0
    else:
        if steel_grade == '250':
            if t <= 8.0:
                f_y_plate = 280.0
            elif t <= 12.0:
                f_y = 260.0
            elif t <= 50.0:
                f_y = 250.0
            elif t <= 80.0:
                f_y = 240.0
            f_u_plate = 410.0
        elif steel_grade == '300':
            if t <= 8.0:
                f_y = 320.0
            elif t <= 12.0:
                f_y = 310.0
            elif t <= 20.0:
                f_y = 300.0
            elif t <= 50.0:
                f_y = 280.0
            elif t <= 80.0:
                f_y = 270.0
            f_u_plate = 410.0
        elif steel_grade == '400':
            if t <= 12.0:
                f_y = 400.0
            elif t <= 20.0:
                f_y = 380.0
            elif t <= 80.0:
                f_y = 360.0
            f_u_plate = 480.0
    return f_y


def plate_tensile_stength(steel_grade: str, t: float, resi_stress_cat) -> float:
    """
    Returns the steel plate element tensile strength 'fu' based on the
    input 'steel grade' and plate thickness.

    steel_grade: Steel grade in accordance with AS/NZS 3678 or AS/NZS 3679.1.
    t: Plate thickness (mm)
    resi_stress_cat: Residual Stress Category for the plate. Used to
        determine categorise the steel element in accordance with
        AS 4100:2020(+A1) Table 2.1.
    """
    if resi_stress_cat == "HR":
        if steel_grade == '250':
            f_u = 410.0
        elif steel_grade == '300':
            f_u = 440.0
        elif steel_grade == '350':
            f_u = 480.0
    else:
        if steel_grade == '250':
            f_u = 410.0
        elif steel_grade == '300':
            f_u = 430.0
        elif steel_grade == '400':
            f_u = 480.0
    return f_u
