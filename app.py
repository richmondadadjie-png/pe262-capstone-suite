import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from engineering import Fluid, Pipe, PipeFlowSystem, HeatTransferModel

st.set_page_config(page_title="Fluid Flow & Heat Transfer Suite", page_icon="⚙️", layout="wide")
st.title("⚙️ Engineering Analysis & Visualization Suite")
st.caption("PE 262 Capstone Application — Multi-Physics Computational Tool")

st.sidebar.header("Navigation")
module_choice = st.sidebar.radio(
    "Select Analysis Module:",
    [
        "Module A: Pipe Flow Analyser",
        "Module B: Heat Transfer Calculator",
        "Module C: Rock & Fluid Data Dashboard",
        "Module D: Code Documentation & Verification"
    ]
)

if module_choice == "Module A: Pipe Flow Analyser":
    st.header("🌊 Module A: Pipe Flow & Pressure Drop Analyser")
    col_side, col_main = st.columns([1, 2])

    with col_side:
        st.subheader("1. Fluid Properties")
        fluid_option = st.selectbox("Fluid Preset", ["Water", "Air", "Crude Oil", "User-Defined"])

        if fluid_option == "User-Defined":
            fluid = Fluid("Custom Fluid", 
                          st.number_input("Density (kg/m³)", value=1000.0, min_value=0.1),
                          st.number_input("Dynamic Viscosity (Pa·s)", value=0.001, min_value=0.000001, format="%.6f"))
        else:
            fluid = Fluid.from_preset(fluid_option)
            st.info(f"**Density:** {fluid.density} kg/m³\n\n**Viscosity:** {fluid.viscosity} Pa·s")

        st.subheader("2. Pipe Geometry")
        diameter_mm = st.number_input("Pipe Inner Diameter (mm)", value=50.0, min_value=1.0)
        length_m = st.number_input("Pipe Length (m)", value=100.0, min_value=0.1)
        roughness_mm = st.number_input("Absolute Roughness (mm)", value=0.045, min_value=0.000, format="%.4f")

        st.subheader("3. Operating Parameters")
        flow_rate_m3h = st.number_input("Volumetric Flow Rate (m³/h)", value=15.0, min_value=0.1)

    with col_main:
        try:
            pipe = Pipe(diameter=diameter_mm/1000.0, length=length_m, roughness=roughness_mm/1000.0)
            system = PipeFlowSystem(fluid=fluid, pipe=pipe)
            results = system.calculate_pressure_drop(flow_rate_m3h / 3600.0)

            st.subheader("Calculation Outputs")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Flow Velocity", f"{results['velocity_m_s']:.2f} m/s")
            m2.metric("Reynolds Number", f"{results['reynolds_number']:,.0f}")
            m3.metric("Friction Factor (f)", f"{results['friction_factor']:.4f}")
            m4.metric("Pressure Drop", f"{results['pressure_drop_kPa']:.2f} kPa")

            st.subheader("System Performance Curve")
            flow_range_m3h = np.linspace(max(0.1, flow_rate_m3h * 0.1), flow_rate_m3h * 2.0, 50)
            dp_list = [system.calculate_pressure_drop(q/3600.0)['pressure_drop_kPa'] for q in flow_range_m3h]

            fig = px.line(pd.DataFrame({"Flow Rate (m³/h)": flow_range_m3h, "Pressure Drop (kPa)": dp_list}),
                          x="Flow Rate (m³/h)", y="Pressure Drop (kPa)", title="Pressure Drop vs. Flow Rate", markers=True)
            fig.add_vline(x=flow_rate_m3h, line_dash="dash", line_color="red", annotation_text="Operating Point")
            st.plotly_chart(fig, use_container_width=True)

            export_df = pd.DataFrame([{
                "Fluid": fluid.name, "Density (kg/m3)": fluid.density, "Viscosity (Pa.s)": fluid.viscosity,
                "Pipe Diameter (mm)": diameter_mm, "Pipe Length (m)": length_m, "Flow Rate (m3/h)": flow_rate_m3h,
                "Velocity (m/s)": results['velocity_m_s'], "Reynolds Number": results['reynolds_number'],
                "Friction Factor": results['friction_factor'], "Pressure Drop (kPa)": results['pressure_drop_kPa']
            }])
            st.download_button("📥 Export Calculation Summary to CSV", export_df.to_csv(index=False).encode('utf-8'),
                               "pipe_flow_summary.csv", "text/csv")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif module_choice == "Module B: Heat Transfer Calculator":
    st.header("🔥 Module B: Heat Transfer Calculator")
    tab1, tab2 = st.tabs(["1. Steady-State Wall Conduction", "2. Transient Newton Cooling"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            k_val = st.number_input("Thermal Conductivity k (W/m·K)", value=45.0, min_value=0.01)
            area_val = st.number_input("Cross-Sectional Area A (m²)", value=2.0, min_value=0.01)
            thick_val = st.number_input("Wall Thickness L (m)", value=0.05, min_value=0.001)
        with c2:
            t1_val = st.number_input("Inside Surface Temp T1 (°C)", value=150.0)
            t2_val = st.number_input("Outside Surface Temp T2 (°C)", value=30.0)

        if st.button("Calculate Conduction Rate"):
            q_watts = HeatTransferModel.wall_conduction(k_val, area_val, thick_val, t1_val, t2_val)
            st.success(f"**Heat Rate (Q):** `{q_watts:,.2f} W` ({q_watts/1000.0:.3f} kW)")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            m_body = st.slider("Body Mass m (kg)", 0.1, 50.0, 2.5, 0.1)
            cp_body = st.slider("Specific Heat Capacity Cp (J/kg·K)", 100, 4200, 500, 50)
            h_coeff = st.slider("Convective Coeff h (W/m²·K)", 5, 250, 25, 5)
        with c2:
            area_body = st.slider("Surface Area A (m²)", 0.01, 2.00, 0.15, 0.01)
            t0_body = st.slider("Initial Temp T0 (°C)", 50, 500, 200, 5)
            t_inf_body = st.slider("Ambient Temp T_inf (°C)", -10, 40, 25, 1)
            t_target_body = st.slider("Target Temp T_target (°C)", int(t_inf_body + 1), int(t0_body - 1), 50, 1)

        try:
            cool_time_s = HeatTransferModel.calculate_cooling_time(m_body, cp_body, h_coeff, area_body, t0_body, t_target_body, t_inf_body)
            st.metric("Time to Reach Target Temp", f"{cool_time_s/60.0:.2f} minutes")
            curve_data = HeatTransferModel.generate_cooling_curve(m_body, cp_body, h_coeff, area_body, t0_body, t_inf_body, cool_time_s * 1.5)
            fig_cool = px.line(curve_data, x="Time (min)", y="Temperature (°C)", title="Transient Cooling Curve")
            fig_cool.add_hline(y=t_inf_body, line_dash="dash", line_color="blue")
            st.plotly_chart(fig_cool, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif module_choice == "Module C: Rock & Fluid Data Dashboard":
    st.header("📊 Module C: Petrophysics Dashboard")
    uploaded_file = st.file_uploader("Upload Petrophysical CSV File", type=["csv"])

    if uploaded_file is None:
        if st.button("Load Sample Petrophysical Dataset"):
            np.random.seed(42)
            porosity = np.random.uniform(0.05, 0.30, 120)
            perm = np.clip(10 ** (15 * porosity - 2) + np.random.normal(0, 5, 120), 0.1, 5000.0)
            df = pd.DataFrame({"Sample_ID": [f"CORE-{i+101}" for i in range(120)], "Porosity_fraction": np.round(porosity, 4), "Permeability_mD": np.round(perm, 2)})
        else:
            df = None
    else:
        df = pd.read_csv(uploaded_file)

    if df is not None:
        st.write("**Dataset Preview**", df.head())
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            filter_col = st.selectbox("Select Filter Parameter", numeric_cols)
            selected_range = st.slider(f"Filter range for {filter_col}", float(df[filter_col].min()), float(df[filter_col].max()), (float(df[filter_col].min()), float(df[filter_col].max())))
            filtered_df = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.histogram(filtered_df, x=numeric_cols[0], title="Distribution Histogram"), use_container_width=True)
            with c2:
                st.plotly_chart(px.scatter(filtered_df, x=numeric_cols[0], y=numeric_cols[1], log_y=True, title="Crossplot"), use_container_width=True)

            st.download_button("📥 Download Filtered CSV", filtered_df.to_csv(index=False).encode('utf-8'), "filtered_data.csv", "text/csv")

elif module_choice == "Module D: Code Documentation & Verification":
    st.header("📝 Module D: Verification & AI Usage Log")
    st.markdown("""
    | # | AI Prompt | Code Generated | Verification | Modification |
    |---|---|---|---|---|
    | 1 | Haaland friction factor | `calculate_friction_factor()` | Verified vs Colebrook-White | Added laminar checks |
    | 2 | Streamlit Plotly heat graph | Cooling curve plot | Verified dynamic sliders | Fixed plot time bounds |
    | 3 | Core dataset generator | Synthetic petrophysics | Confirmed Kozeny-Carman trend | Added non-negative caps |
    """)