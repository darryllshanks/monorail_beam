import streamlit as st
import plotly.graph_objects as go
import monorail_beam_app_module as mba_mod
from handcalcs.decorator import handcalc
from plotly import graph_objects as go
from monorail_beam import utils


st.header("Monorail Beam Design to DR AS 1418.18:2023")

sb_expander_1 = st.sidebar.expander(label="Project Details")
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
    hoisting_class = st.selectbox("Hoisting Class", hoisting_classes, placeholder="HC4",)
    max_steady_hoist_speed = st.number_input("Maximum Steady Hoisting Speed (m/min)", value=20.0, min_value=0.0, step=0.1)
    steady_hoist_creep_speed = st.number_input("Steady Hoisting Creed Speed (m/min)", value=2.0, min_value=0.0, step=0.1)
    n_cycles = st.number_input("Design Number of Full Load Cycles", value=1000, min_value=0, step=1)

sb_expander_3 = st.sidebar.expander(label="Flange Wheel Loading")
with sb_expander_3:
    st.image("monorail_beam/images/wheel_flange_loading.png", width=100, )
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

tab0, tab1, tab2, tab3 = st.tabs(["Readme","Monorail Geometry", "Results Diagrams", "Beam Design"])

# Setup and formatting of 'Readme' tab
with tab0:
    st.markdown("#### Purpose")
    st.write(
        "This objective of this app is to provide structural engineers with a simple " +
        "tool to check a simple monorail beam with a single hoist. The user may input " +
        "a monorail beam with either 1 or 2 spans supported at both ends, with " +
        "the possibility of adding a cantilever on the right hand side.")

    st.markdown("#### Disclaimer")
    st.write(
        "This app has been based on the revised design requirements for monorails per " +
        "the DRAFT copy of AS 1418.18:2023, that is currently released for public comment. " +
        "Any design results are for information only and shall not be used for the purposes " +
        "of issuing or certifying the design of monorail beams.")

    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True) 
    
    st.markdown("#### Assumptions and Limitations")
    st.write("- Only straight monorails are considered. Curved monorails are beyond the scope of this app")
    st.write("- The monorail beam is assumed to be a single beam of I-Section geometry")
    st.write("- Only Australian steel sizes and grades are currently available")
    st.write("- Conservatively, alpha_m has been set as 1.0. Future revisions may allow the user " +
             "to provide this manually for each span.")
    st.write("- The factor K_L needs to be set manually to suit the location of input moment")

    st.markdown("#### Exclusions")
    st.write("- The assessment of connections at the monorail support points")
    st.write("- Fatigue design")
    st.write("- Addition of flange plates to the bottom flange to improve local flange bending")
    st.write("- Out-of-plane stiffness for 4% min. lateral load is not calculated")

    st.markdown("#### Current 'Work in Progress' Items")
    st.write("- Ability to add bottom flange strengthening plates.")
    st.write("- Option to automatically determine the location max/min deflections " +
             "and pass through to deflection checks. Currently this is done manually.")
    st.write("- Option to automatically pass the calculated moments through the design " +
             "checks. Currently only manual input to allow flexibility with other software.")
    st.write("- Beam shear is not currently checked, though this is rarely a governing factor " +
             "for the design of monorail beams. Will be added for completeness.")

# Setup and formatting of 'Monorail Geometry' tab
with tab1:
    st.image("monorail_beam/images/monorail_visual.png")

    col_1_1, col_1_2 = st.columns(2)
    with col_1_1:
        num_of_end_spans = st.number_input("Number of Internal Spans with Supports at Both Ends", value=1, min_value=1, max_value=2, step=1)
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

# Setup and formatting of 'Results Diagrams' tab
with tab2:
    st.markdown("#### Position of Point Load")
    st.write(
        "The slider below moves the position of the point load for the purposes of checking deflections " +
        "at a given point as these are not solved in an envelope. The bending moment and shear force " +
        "diagrams overlay the design action curves generated from moving the hoist along the beam.")
    hoist_pos = st.slider("Position of Point Load",min_value=0, max_value=total_length, step=50, label_visibility='hidden')
    
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
    static_results, env_results, sb_data = mba_mod.run_analysis(app_inputs=inputs)

    # Extracts the max and min design actions from the envelope critical values dict
    M_max_val = utils.round_up(env_results['ULS']['Critical Values']['Mmax']['val'], 2)
    M_max_pos = env_results['ULS']['Critical Values']['Mmax']['at']
    M_min_val = utils.round_up(env_results['ULS']['Critical Values']['Mmin']['val'], 2)
    M_min_pos = env_results['ULS']['Critical Values']['Mmin']['at']

    V_max_val = utils.round_up(env_results['ULS']['Critical Values']['Vmax']['val'], 2)
    V_max_pos = env_results['ULS']['Critical Values']['Vmax']['at']
    V_min_val = utils.round_up(env_results['ULS']['Critical Values']['Vmin']['val'], 2)
    V_min_pos = env_results['ULS']['Critical Values']['Vmin']['at']

    # R1_max_val = utils.round_up(env_results['ULS']['Critical Values']['Rmax0']['val'], 2)
    # R2_max_val = utils.round_up(env_results['ULS']['Critical Values']['Rmax1']['val'], 2)
    # R3_max_val = utils.round_up(env_results['ULS']['Critical Values']['Rmax2']['val'], 2)

    # st.write(env_results['ULS']['Critical Values'])

    tab2_expander_1 = st.expander(label="Bending Moment Diagram",expanded=True)
    with tab2_expander_1 :
        # Generates moment envelope diagram with overlay of static load case
        x_val_M_env = env_results['ULS']['Matrixes']['x_dist']
        y_val_Mmax_env = env_results['ULS']['Matrixes']['Mmax']
        y_val_Mmin_env = env_results['ULS']['Matrixes']['Mmin']

        x_val_M = static_results['ULS']['Matrixes']['x_dist']
        y_val_M = static_results['ULS']['Matrixes']['Moment']

        fig_moment = go.Figure()
        fig_moment.add_trace(go.Scatter(x=x_val_M_env, y=y_val_Mmin_env, line={'color': 'rgb(255,0,0)', 'width': 3}, fill='tozeroy'))
        fig_moment.add_trace(go.Scatter(x=x_val_M_env, y=y_val_Mmax_env, line={'color': 'rgb(0,0,255)', 'width': 3}, fill='tozeroy'))
        fig_moment.add_trace(go.Scatter(x=x_val_M, y=y_val_M, line={'color': 'rgb(255,255,255)', 'width': 3}))
        # Adds text annotations for max and min to graph
        fig_moment.add_trace(go.Scatter(x=[M_min_pos], y=[M_min_val], mode="text", name="Mmin", text=f"Mmin: {M_min_val} kNm", textposition="top center",))
        fig_moment.add_trace(go.Scatter(x=[M_max_pos], y=[M_max_val], mode="text", name="Mmax", text=f"Mmax: {M_max_val} kNm", textposition="bottom center"))
       
        fig_moment.layout.width = 650
        fig_moment.layout.height = 400
        fig_moment.layout.title.text = "Bending Moment Envelope"
        fig_moment.layout.xaxis.title = "Distance, x (m)"
        fig_moment.layout.yaxis.title = "Bending Moment (kNm)"
        fig_moment.update_layout(showlegend=False)
        fig_moment.update_yaxes(autorange="reversed")
        fig_moment

    tab2_expander_2 = st.expander(label="Shear Force Diagram", expanded=False)
    with tab2_expander_2:
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
        # Adds text annotations for max and min to graph
        fig_shear.add_trace(go.Scatter(x=[V_min_pos], y=[V_min_val], mode="text", name="Vmin", text=f"Vmin: {M_min_val} kNm", textposition="top center",))
        fig_shear.add_trace(go.Scatter(x=[V_max_pos], y=[V_max_val], mode="text", name="Vmin", text=f"Vmax: {M_max_val} kNm", textposition="bottom center"))

        fig_shear.layout.width = 650
        fig_shear.layout.height = 400
        fig_shear.layout.title.text = "Shear Force Envelope"
        fig_shear.layout.xaxis.title = "Distance, x (m)"
        fig_shear.layout.yaxis.title = "Shear Force (kN)"
        fig_shear.update_layout(showlegend=False)
        fig_shear

    beam_cont_defl_lim_upper = max(beam_span_1, beam_span_2)  / 300
    beam_cont_defl_lim_lower = -max(beam_span_1, beam_span_2) / 300 

    beam_cant_defl_lim_upper = cant_span_R  / 500
    beam_cant_defl_lim_lower = -cant_span_R / 500 

    tab2_expander_3 = st.expander(label="# Deflection Diagram", expanded=False)
    with tab2_expander_3:
        # Generates deflection diagram for specific static load case
        x_val_D = static_results['SLS']['Matrixes']['x_dist']
        y_val_D = static_results['SLS']['Matrixes']['Deflections'] * 1000
        fig_defl = go.Figure()
        fig_defl.add_trace(go.Scatter(x=x_val_D, y=y_val_D, line={'color': 'rgb(255,0,0)', 'width': 3}))
        # fig_defl.add_trace(go.Scatter(x=[0, (beam_span_1+beam_span_2) * 1e-3], y=[beam_cont_defl_lim_lower, beam_cont_defl_lim_lower], line={'color': 'rgb(255,0,0)', 'width': 3}))
        # fig_defl.add_trace(go.Scatter(x=[(beam_span_1+beam_span_2) * 1e-3, (beam_span_1+beam_span_2+cant_span_R) * 1e-3], y=[beam_cant_defl_lim_lower, beam_cant_defl_lim_lower], line={'color': 'rgb(255,0,0)', 'width': 3}))
        fig_defl.layout.width = 650
        fig_defl.layout.width = 650
        fig_defl.layout.height = 400
        fig_defl.layout.title.text = "Deflection Diagram"
        fig_defl.layout.xaxis.title = "Distance, x (m)"
        fig_defl.layout.yaxis.title = "Deflection (mmm)"
        fig_defl.update_layout(showlegend=False)
        fig_defl.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor="white",dtick=1, ticklabelstep=2)
        fig_defl
        
        defl_max = static_results['SLS']['Critical Values']['Deflections'][0]
        st.write(f"Max Deflection: {utils.round_up(defl_max,2)} mm")

        defl_min = static_results['SLS']['Critical Values']['Deflections'][1]
        st.write(f"Min Deflection: {utils.round_up(defl_min,2)} mm")

# Setup and formatting of 'Beam Design' tab
with tab3:
    st.markdown("#### Bending Moment Input")
    st.write(
        "Instead of automatically passing through the design actions, the user is required to input " +
        "the design actions desired to be checked. This is to provide flexibility if the design actions " +
        "have been calculated using other software")
    M_max_cont = st.number_input("Maximum Bending Moment in Continuous Beam / Backspan (kNm)", value=0.0, min_value=0.0)
    if cant_span_R != 0:
        M_max_cant = st.number_input("Maximum Bending Moment in Cantilevered Beam (kNm)", value=0.0, min_value=0.0)
    else:
        M_max_cant = 0
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    st.markdown("#### Global Bending Capacity Checks")
    beam_design_results = mba_mod.beam_capacity(app_inputs=inputs, sb=sb_data)
    st.markdown("##### Span 1")
    col_3_1, col_3_2, col_3_3 = st.columns([3,1,3])

    with col_3_1:
        st.write(f"Effective Length, le =")
        st.write(f"Alpha_m =")
        st.write(f"Member Bending Capacity, $phi.M_bx$ =")
    with col_3_2:
        st.write(f"{utils.round_up(beam_design_results['Span 1']['l_e'], 2)} mm")
        st.write(f"{utils.round_up(beam_design_results['Span 1']['alpha_m'], 2)}")
        st.write(f"{utils.round_down(beam_design_results['Span 1']['M_bx']* 1e-6, 2)} kNm")
    with col_3_3:
        st.write(".")
        st.write(".")
        if utils.round_down(beam_design_results['Span 1']['M_bx'] * 1e-6, 2)  < M_max_cont:
            st.write(f":red[NOT OK: Member Bending Capacity Exceeded.]")
        else:
            st.write(f":green[OK: Member Bending Capacity is Adequate.]")

    if beam_span_2 != 0:
        st.markdown("##### Span 2")
        col_3_4, col_3_5, col_3_6 = st.columns([3,1,3])
        with col_3_4:
            st.write(f"Effective Length, le =")
            st.write(f"Alpha_m =")
            st.write(f"Member Bending Capacity, $phi.M_bx$ =")
        with col_3_5:
            st.write(f"{utils.round_up(beam_design_results['Span 2']['l_e'], 2)} mm")
            st.write(f"{utils.round_up(beam_design_results['Span 2']['alpha_m'], 2)}")
            st.write(f"{utils.round_down(beam_design_results['Span 2']['M_bx']* 1e-6, 2)} kNm")
        with col_3_6:
            st.write(".")
            st.write(".")
            if utils.round_down(beam_design_results['Span 2']['M_bx'] * 1e-6, 2)  < M_max_cont:
                st.write(f":red[NOT OK: Member Bending Capacity Exceeded.]")
            else:
                st.write(f":green[OK: Member Bending Capacity is Adequate.]")

    if cant_span_R != 0:
        st.markdown("##### Cantilever Span")
        col_3_7, col_3_8, col_3_9 = st.columns([3,1,3])
        with col_3_7:
            st.write(f"Effective Length, le =")
            st.write(f"Alpha_m =")
            st.write(f"Member Bending Capacity, $phi.M_bx$ =")
        with col_3_8:
            st.write(f"{utils.round_up(beam_design_results['Span 3']['l_e'], 2)} mm")
            st.write(f"{utils.round_up(beam_design_results['Span 3']['alpha_m'], 2)}")
            st.write(f"{utils.round_down(beam_design_results['Span 3']['M_bx']* 1e-6, 2)} kNm")
        with col_3_9:
            st.write(".")
            st.write(".")
            if utils.round_down(beam_design_results['Span 3']['M_bx'] * 1e-6, 2)  < M_max_cont:
                st.write(f":red[NOT OK: Member Bending Capacity Exceeded.]")
            else:
                st.write(f":green[OK: Member Bending Capacity is Adequate.]")
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

    st.markdown("#### Local Checks")
    M_max_dyn = st.number_input("Maximum Dynamically Factored Bending Moment at Location of Wheel Load (kNm)", value=0.0, min_value=0.0)
    n_wheel = wheel_load_dist * sb_data.Q_load_dls * 1e-2
    bending_stress = M_max_dyn * 1e6 / sb_data.Z_x
    load_pos_fact_list = ['1.0', '1.3']
    K_L = st.selectbox("Load Position Factor, $K_L$", load_pos_fact_list, placeholder='1.3')
    min_flg_thk, min_web_thk = mba_mod.calc_min_element_thickness(
        N_W=n_wheel,
        f_y=min(sb_data.yield_stress_flg(), sb_data.yield_stress_web()),
        D=sb_data.d,
        f_b=bending_stress,
        K_L=utils.str_to_float(K_L),
        C_F=cf_bf * sb_data.b_f * 0.5,
        B_F=sb_data.b_f * 0.5,
        n_cycles=n_cycles
    )

    col_3_10, col_3_11, col_3_12 = st.columns([3,1,3])
    with col_3_10:
        st.write(f"Maximum Dynamic Wheel Load, N_w =")
        st.write(f"Dynamically Factored Bending Stress, f_b =")
        st.write(f"Min Flange Thickness Required, tf.min =")
        st.write(f"Monorail Beam Flange Thickness, tf =")
        st.write(f"Min Web Thickness Required, tw.min =")
        st.write(f"Monorail Beam Web Thickness, tw =")
    with col_3_11:
        st.write(f"{utils.round_up(n_wheel, 2)} kN")
        st.write(f"{utils.round_up(bending_stress, 2)} MPa")
        st.write(f"{utils.round_up(min_flg_thk, 1)} mm")
        st.write(f"{utils.round_up(sb_data.t_f, 1)} mm")
        st.write(f"{utils.round_up(min_web_thk, 1)} mm")
        st.write(f"{utils.round_up(sb_data.t_w, 1)} mm")
    with col_3_12:
        st.write(".")
        st.write(".")
        st.write(".")
        if min_flg_thk > sb_data.t_f:
            st.write(f":red[NOT OK: Increase flange thickness.]")
        else:
            st.write(f":green[OK: Flange thickness is adequate.]")
        st.write(".")
        if min_web_thk > sb_data.t_w:
            st.write(f":red[NOT OK: Increase web thickness.]")
        else:
            st.write(f":green[OK: Web thickness is adequate.]")
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
 
    st.markdown("#### Deflection Checks")
    st.write("Deflections to be manually input in the fields below for checks against deflection limits. " +
             "Deflections shall be input as absolute/positive values.")
    if beam_span_2 != 0:
        defl_max_span_1 = st.number_input("Maximum Deflection in Beam Span 1 (mm)", value=0.0, min_value=0.0)
        defl_max_span_2 = st.number_input("Maximum Deflection in Beam Span 2 (mm)", value=0.0, min_value=0.0)
    else:
        defl_max_span_1 = st.number_input("Maximum Deflection in Continuous Beam / Backspan (mm)", value=0.0, min_value=0.0)
    if cant_span_R != 0:
        defl_max_cant = st.number_input("Maximum Deflection in Cantilevered Beam (mm)", value=0.0, min_value=0.0)
    else:
        defl_max_cant = 0

    col_3_13, col_3_14, col_3_15 = st.columns([3,1,3])
    with col_3_13:
        if beam_span_2 != 0:
            st.write(f"Beam Span 1 Deflection Limit, d.lim =")
            st.write(f"Beam Span 2 Deflection Limit, d.lim =")
        else:
            st.write(f"Beam / Backspan Deflection Limit, d.lim =")
        if cant_span_R != 0:
            st.write(f"Cantilever Deflection Limit, d =")
    with col_3_14:
        if beam_span_2 != 0:
            st.write(f"{beam_span_1 / 500} mm")
            st.write(f"{beam_span_2 / 500} mm")
        else:
            st.write(f"{beam_span_1 / 500} mm")
        if cant_span_R != 0:
            st.write(f"{cant_span_R / 300} mm")
    with col_3_15:
        if defl_max_span_1 > (beam_span_1/ 500):
            st.write(f":red[NOT OK: Deflection exceeds limit of SPAN / 500.]")
        else:
            st.write(f":green[OK: Deflections are below acceptable limits.]")
        if beam_span_2 != 0:
            if defl_max_span_1 > (beam_span_2/ 500):
                st.write(f":red[NOT OK: Deflection exceeds limit of SPAN / 500.]")
            else:
                st.write(f":green[OK: Deflections are below acceptable limits.]")
        if cant_span_R != 0:
            if defl_max_cant > (cant_span_R / 300):
                st.write(f":red[NOT OK: Deflection exceeds limit of SPAN / 300.]")
            else:
                st.write(f":green[OK: Deflections are below acceptable limits.]")



# Checks for input and structured_data dictionaries
# st.write(inputs)
# st.write(sb_data)
# st.write(str_beam_data)
# st.write(beam_design_results)

