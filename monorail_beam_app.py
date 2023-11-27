import streamlit as st
import plotly.graph_objects as go
import monorail_beam_app_module as mba_mod
from handcalcs.decorator import handcalc
from plotly import graph_objects as go

st.header("Monorail Beam Design to DR AS 1418.18:2023")

sb_expander_1 = st.sidebar.expander(label="# Project Details")
with sb_expander_1:
    proj_num = st.text_input("Project Number")
    proj_name = st.text_input("Project Name")
    beam_name = st.text_input("Monorail Name / ID")

sb_expander_2 = st.sidebar.expander(label="# Hoist Inputs")
# st.sidebar.markdown("# Hoist Inputs")
with sb_expander_2:
    mrc = st.number_input("MRC (t)", value=2.0, min_value=0.0, step=0.1)
    hoist_mass = st.number_input("Trolley and Motor Mass (kg)", value=300, min_value=0, step=10)
    hoist_drive_classes = ["HD1", "HD2", "HD3", "HD4", "HD5"]
    hoist_drive_class = st.selectbox("Hoist Drive Class", hoist_drive_classes, placeholder="HD1")
    hoisting_classes = ["HC1", "HC2", "HC3", "HC4"]
    hoisting_class = st.selectbox("Hoisting Class", hoisting_classes, placeholder="HC4")
    max_steady_hoist_speed = st.number_input("Maximum Steady Hoisting Speed (m/min)", value=20.0, min_value=0.0, step=0.1)
    steady_hoist_creep_speed = st.number_input("Steady Hoisting Creed Speed (m/min)", value=2.0, min_value=0.0, step=0.1)
    n_cycles = st.number_input("Design Number of Full Load Cycles", value=1000, min_value=0, step=1)

sb_expander_3 = st.sidebar.expander(label="Flange Wheel Loading")
with sb_expander_3:
    st.image("images/wheel_flange_loading.png", width=100, )
    cf_bf = st.number_input("Ratio of $C_F / B_F$", value=0.9, min_value=0.0, max_value=1.0, step=0.01)
    wheel_load_dist = st.number_input("Maximum Static Wheel as Percentage of Total Load", value=45, min_value=0, max_value=50, step=1)

sb_expander_4 = st.sidebar.expander(label="Steel Inputs")
with sb_expander_4:
    beam_type = st.selectbox("Beam Type", ["UB", "UC", "WB", "WC"])
    section_list = mba_mod.section_list(beam_type)
    section_size = st.selectbox("Selected Section", section_list)

    if beam_type == "UB" or beam_type == "UC":
        HR_steel_grades = ["250", "300", "350"]
        steel_grade = st.selectbox("Steel Grade", HR_steel_grades, placeholder="300")
    else:
        HW_steel_grades = ["250", "300", "400"]
        steel_grade = st.selectbox("Steel Grade", HW_steel_grades, placeholder="300")


tab1, tab2, tab3 = st.tabs(["Monorail Geometry", "Results Diagrams", "Beam Design"])

with tab1:
    st.image("images/monorail_visual.png")

    col_1_1, col_1_2 = st.columns(2)
    with col_1_1:
        num_of_end_spans = st.number_input("Number of Internal Spans with Supports at Both Ends", value=2, min_value=1, max_value=2, step=1)
    with col_1_2:
        cant_right = st.toggle("Cantilever on Right-Hand Side")

    col_1_3, col_1_4 = st.columns(2)
    with col_1_3:
        if num_of_end_spans == 1:
            beam_span_1 = st.number_input("Beam Span / Backspan (mm)", value=4000, min_value=0, step=50)
            beam_span_2 = 0
            support_rest = {0.0: "P", beam_span_1: "R"}
        elif num_of_end_spans == 2:
            beam_span_1 = st.number_input("Beam Span No. 1 (mm)", value=4000, min_value=0, step=50)
            beam_span_2 = st.number_input("Beam Span No. 2 (mm)", value=4000, min_value=0, step=50)
            support_rest = {0.0: "P", beam_span_1: "R", beam_span_1 + beam_span_2: "R"}
        
        if cant_right == True:
            cant_span_R = st.number_input("RHS Cantilever Span (mm)", value=2000, min_value=0, step=50)
        else:
            cant_span_R = 0
        
    with col_1_4:
        int_restraint_types = ["FF", "FP", "PP"]
        cant_restraint_types = ["FU", "PU"]
        if num_of_end_spans == 1:
            seg_1_restraint = st.selectbox("Beam Span / Backspan Restraint Arrangement", int_restraint_types, placeholder="FF")
            seg_2_restraint = "FF"
        elif num_of_end_spans == 2:
            seg_1_restraint = st.selectbox("Beam Span No. 1 Restraint Arrangement", int_restraint_types, placeholder="FF")
            seg_2_restraint = st.selectbox("Beam Span No. 2 Restraint Arrangement", int_restraint_types, placeholder="FF")
        
        if cant_right == True:
            cant_R_restraint = st.selectbox("RHS Cantilever Restraint Arrangement", cant_restraint_types, placeholder="FU")
        else:
            cant_R_restraint = "FU"

# Create a dictionary of all the inputs and passes to the monorail beam_app_module
total_length = beam_span_1 + beam_span_2 + cant_span_R

with tab2:
    hoist_pos = st.slider("Position of Point Load",min_value=0, max_value=total_length, step=10)
    inputs = {
        "Project Details": {"Project No": proj_num, "Project Name": proj_name,"Beam Name": beam_name}, 
        "Loads": {"G_load": hoist_mass * 9.81 / 1000, "Q_load": mrc * 9.81}, # Converts input mass to loads in kN
        "Load Position": hoist_pos,
        "Hoist Data": {
            "HD_Class": hoist_drive_class,
            "HC_Class": hoisting_class,
            "Max Steady Hoist Speed": max_steady_hoist_speed / 60,
            "Steady Hoist Creep Speed": steady_hoist_creep_speed / 60,
            "Wheel Load Dist": wheel_load_dist,
            "Peak Loading Cycles": n_cycles
        },
        "Geometry": {
            "Span 1": {"Span": beam_span_1, "Restraint": seg_1_restraint},
            "Span 2": {"Span": beam_span_2, "Restraint": seg_2_restraint},
            "Span 3": {"Span": cant_span_R, "Restraint": cant_R_restraint}
        },
        "Cantilever": cant_right,
        "Supports": support_rest,
        "Total Length": total_length,
        "Steel Data": {"Steel Grade": steel_grade, "Section Size": section_size}
    }

    static_results, env_results, str_beam_data = mba_mod.run_analysis(app_inputs=inputs)

    # x_val = analysis_results[0][0].x
    # M_min_val = analysis_results[0][0].Mmin
    # M_max_val = results_env.Mmax
    # V_min_val = results_env.Vmin
    # V_max_val = results_env.Vmax

    # st.write(static_results['ULS']['Critical Values']['Moments'])

    # Generates moment envelope diagram with overlay of static load case
    x_val_M_env = env_results['ULS']['Matrixes']['x_dist']
    y_val_Mmax_env = env_results['ULS']['Matrixes']['Mmax']
    y_val_Mmin_env = env_results['ULS']['Matrixes']['Mmin']

    x_val_M = static_results['ULS']['Matrixes']['x_dist']
    y_val_M = static_results['ULS']['Matrixes']['Moment']

    fig_moment = go.Figure()
    fig_moment.add_trace(go.Scatter(x=x_val_M_env, y=-y_val_Mmin_env, line={'color': 'rgb(255,0,0)', 'width': 3}, fill='tozeroy'))
    fig_moment.add_trace(go.Scatter(x=x_val_M_env, y=-y_val_Mmax_env, line={'color': 'rgb(0,0,255)', 'width': 3}, fill='tozeroy'))
    fig_moment.add_trace(go.Scatter(x=x_val_M, y=-y_val_M, line={'color': 'rgb(255,255,255)', 'width': 3}))
    fig_moment.layout.width = 750
    fig_moment.layout.height = 400
    fig_moment.layout.title.text = "Bending Moment Envelope"
    fig_moment.layout.xaxis.title = "Distance, x (m)"
    fig_moment.layout.yaxis.title = "Bending Moment (kNm)"
    fig_moment

    # Generates shear envelope diagram with overlay of static load case
    x_val_V_env = env_results['ULS']['Matrixes']['x_dist']
    y_val_Vmax_env = env_results['ULS']['Matrixes']['Vmax']
    y_val_Vmin_env = env_results['ULS']['Matrixes']['Vmin']
    x_val_V = static_results['ULS']['Matrixes']['x_dist']
    y_val_V = static_results['ULS']['Matrixes']['Shear']
    fig_shear = go.Figure()
    fig_shear.add_trace(go.Scatter(x=x_val_V_env, y=y_val_Vmin_env, line={'color': 'rgb(255,0,255)', 'width': 3}, fill='tozeroy'))
    fig_shear.add_trace(go.Scatter(x=x_val_V_env, y=y_val_Vmax_env, line={'color': 'rgb(124,252,0)', 'width': 3}, fill='tozeroy'))
    fig_shear.add_trace(go.Scatter(x=x_val_V, y=y_val_V, line={'color': 'rgb(255,255,255)', 'width': 3}))
    fig_shear.layout.width = 750
    fig_shear.layout.height = 400
    fig_shear.layout.title.text = "Shear Force Envelope"
    fig_shear.layout.xaxis.title = "Distance, x (m)"
    fig_shear.layout.yaxis.title = "Shear Force (kN)"
    fig_shear

    # Generates deflection diagram for specific static load case
    x_val_D = static_results['ULS']['Matrixes']['x_dist']
    y_val_D = static_results['ULS']['Matrixes']['Deflections'] * 1000
    fig_defl = go.Figure()
    fig_defl.add_trace(go.Scatter(x=x_val_D, y=y_val_D, line={'color': 'rgb(255,255,255)', 'width': 3}))
    fig_defl.layout.width = 750
    fig_defl.layout.height = 400
    fig_defl.layout.title.text = "Deflection Diagram"
    fig_defl.layout.xaxis.title = "Distance, x (m)"
    fig_defl.layout.yaxis.title = "Deflection (mmm)"
    fig_defl
    
    st.write(f"Max Deflection: {static_results['ULS']['Critical Values']['Deflections'][0]}")
    st.write(f"Min Deflection: {static_results['ULS']['Critical Values']['Deflections'][1]}")

    # st.write(inputs)

with tab3:
    my_slider = st.slider("My slider")
    # calc_expander_a = st.expander(label="Design Loads")
    # with calc_expander_a:
    #     st.write()

# flg_thickness = mb_am.mb_flg_thickness()
# st.write(flg_thickness)

# latex_ex, min_flg_thickness = mb_am.mb_flg_thickness


# calc_expander_a = st.expander(label="Minimum Flange Thickness")
# with calc_expander_a:
#     st.latex(latex_ex)


st.write(str_beam_data)



# def create_shear_diagram():
#     """
    
#     """
#     fig_shear = go.Figure()
#     fig_shear.add_trace(go.Scatter(x=x_val, y=V_min_val, line={'color': 'rgb(255,0,255)', 'width': 3}, fill='tozeroy'))
#     fig_shear.add_trace(go.Scatter(x=x_val, y=V_max_val, line={'color': 'rgb(124,252,0)', 'width': 3}, fill='tozeroy'))
#     fig_shear.layout.width = 900
#     fig_shear.layout.height = 600
#     fig_shear.layout.title.text = "Shear Force Envelope"
#     fig_shear.layout.xaxis.title = "Distance, x (m)"
#     fig_shear.layout.yaxis.title = "Shear Force (kN)"
#     fig_shear