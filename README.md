# PE 262 Capstone: Engineering Analysis Suite

A multi-page Streamlit web application for fluid flow analysis, heat transfer calculations, and petrophysical data visualization.

## AI Usage Audit Log

| # | AI Prompt Provided | Code / Feature Generated | Verification Performed | Modifications Made |
|---|-------------------|--------------------------|------------------------|--------------------|
| **1** | "Generate a Haaland equation function in Python for turbulent friction factor calculation." | `calculate_friction_factor()` function in `engineering.py`. | Checked results against explicit Colebrook-White iterative solutions for Re = 10^5. | Added defensive checks for laminar regime (Re < 2300) so f = 64/Re is automatically used. |
| **2** | "Write a Streamlit layout using columns and Plotly to graph real-time transient heat cooling." | Plotly transient line chart updating from slider inputs in `app.py`. | Verified that lowering mass or increasing surface area correctly speeds up cooling curve decay. | Added dynamic plot duration bounds (1.5 x t_target) to prevent plot truncation. |
| **3** | "Create a synthetic petrophysical dataset generator for porosity and permeability." | Core analysis dataset generator script. | Confirmed Kozeny-Carman exponential trends between porosity and log-permeability. | Added clipped bounds (0.1 to 5000 mD) to remove non-physical negative permeability values. |
docs: update README with project description and AI audit table
