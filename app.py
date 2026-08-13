import streamlit as st

st.set_page_config(
    page_title="Variable Pay Simulation",
    page_icon="💼",
    layout="wide"
)

st.title("Variable Pay Simulation Model")

st.write(
    "Professional HR Compensation Planning & Simulation Tool"
)

st.divider()

st.subheader("Simulation Controls")

company_performance = st.slider(
    "Company Performance (%)",
    min_value=90,
    max_value=110,
    value=100,
    step=5
)

target_variable_pay = st.slider(
    "Target Variable Pay (%)",
    min_value=5,
    max_value=20,
    value=12,
    step=1
)

budget = st.number_input(
    "Variable Pay Budget (₹)",
    min_value=1000000,
    max_value=100000000,
    value=30000000,
    step=1000000
)

st.divider()

st.write("Selected Simulation Inputs")

st.write(
    f"Company Performance: {company_performance}%"
)

st.write(
    f"Target Variable Pay: {target_variable_pay}%"
)

st.write(
    f"Variable Pay Budget: ₹{budget:,.0f}"
)
