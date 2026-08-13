import streamlit as st
import pandas as pd
import numpy as np
# ============================================================
# SESSION STATE
# ============================================================

if "simulation" not in st.session_state:
    st.session_state.simulation = None

if "simulation_run" not in st.session_state:
    st.session_state.simulation_run = False

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Variable Pay Simulation",
    page_icon="💼",
    layout="wide"
)
# ============================================================
# PROFESSIONAL APPLICATION STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* Main application spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 4rem;
        padding-right: 4rem;
    }

    /* Main headings */
    h1 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h2 {
        font-weight: 650;
        margin-top: 2rem;
    }

    h3 {
        font-weight: 600;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 500;
    }

    [data-testid="stMetricValue"] {
        font-weight: 650;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 7px;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
    }

    /* Divider */
    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# MODEL SETUP
# ============================================================

np.random.seed(42)

N_EMPLOYEES = 500

VARIABLE_PAY_BUDGET = 30_000_000

MIN_PERFORMANCE_THRESHOLD = 50

MAX_PAYOUT_MULTIPLIER = 1.50


# ============================================================
# DEPARTMENTS
# ============================================================

departments = [
    "Sales",
    "Finance",
    "Human Resources",
    "Marketing",
    "Operations",
    "Technology",
    "Customer Success"
]

department_weights = [
    0.20,
    0.12,
    0.08,
    0.12,
    0.18,
    0.18,
    0.12
]


# ============================================================
# JOB LEVELS
# ============================================================

job_levels = [
    "Entry",
    "Junior",
    "Mid",
    "Senior",
    "Manager"
]

job_level_weights = [
    0.18,
    0.22,
    0.30,
    0.20,
    0.10
]


# ============================================================
# SALARY STRUCTURE
# ============================================================

salary_ranges = {
    "Entry": (300000, 450000),
    "Junior": (400000, 600000),
    "Mid": (550000, 850000),
    "Senior": (800000, 1200000),
    "Manager": (1100000, 1800000)
}


# ============================================================
# TARGET VARIABLE PAY BY JOB LEVEL
# ============================================================

target_variable_pay = {
    "Entry": 0.05,
    "Junior": 0.08,
    "Mid": 0.12,
    "Senior": 0.18,
    "Manager": 0.25
}


# ============================================================
# DEPARTMENT FACTORS
# ============================================================

department_bonus_factor = {
    "Sales": 1.05,
    "Finance": 1.00,
    "Human Resources": 0.95,
    "Marketing": 1.00,
    "Operations": 0.98,
    "Technology": 1.03,
    "Customer Success": 1.02
}


# ============================================================
# CREATE SYNTHETIC WORKFORCE
# ============================================================

employee_ids = [
    f"EMP{str(i).zfill(4)}"
    for i in range(1, N_EMPLOYEES + 1)
]

df = pd.DataFrame({
    "Employee_ID": employee_ids,

    "Department": np.random.choice(
        departments,
        size=N_EMPLOYEES,
        p=department_weights
    ),

    "Job_Level": np.random.choice(
        job_levels,
        size=N_EMPLOYEES,
        p=job_level_weights
    )
})


# ============================================================
# BASE SALARY
# ============================================================

df["Base_Salary"] = df["Job_Level"].apply(
    lambda level: np.random.randint(
        salary_ranges[level][0],
        salary_ranges[level][1] + 1
    )
)


# ============================================================
# TARGET VARIABLE PAY
# ============================================================

df["Target_Variable_Pay_Pct"] = (
    df["Job_Level"].map(target_variable_pay)
)


# ============================================================
# PERFORMANCE VARIABLES
# ============================================================

df["Individual_Performance"] = np.clip(
    np.random.normal(75, 12, N_EMPLOYEES),
    40,
    100
).round(2)

df["Goal_Achievement"] = np.clip(
    np.random.normal(78, 14, N_EMPLOYEES),
    40,
    110
).round(2)

df["Competency_Score"] = np.clip(
    np.random.normal(76, 10, N_EMPLOYEES),
    40,
    100
).round(2)

df["Company_Performance"] = np.clip(
    np.random.normal(82, 8, N_EMPLOYEES),
    50,
    100
).round(2)


# ============================================================
# NORMALIZE GOAL ACHIEVEMENT
# ============================================================

df["Goal_Achievement_Normalized"] = np.minimum(
    df["Goal_Achievement"],
    100
)


# ============================================================
# DEPARTMENT FACTOR
# ============================================================

df["Department_Factor"] = (
    df["Department"].map(department_bonus_factor)
)


# ============================================================
# PAYOUT MULTIPLIER FUNCTION
# ============================================================

def calculate_payout_multiplier(score):

    if score < 50:
        return 0.00

    elif score < 60:
        return 0.50

    elif score < 70:
        return 0.75

    elif score < 80:
        return 1.00

    elif score < 90:
        return 1.25

    else:
        return 1.50


# ============================================================
# SIMULATION ENGINE
# ============================================================

def generate_final_simulation(
    company_performance,
    target_variable_pay,
    selected_budget,
    selected_threshold,
    selected_max_payout
):

    simulation = df.copy()

    # --------------------------------------------------------
    # COMPANY PERFORMANCE ADJUSTMENT
    # --------------------------------------------------------

    company_change = (
        company_performance
        - df["Company_Performance"].mean()
    )

    simulation["Simulated_Company_Performance"] = (
        simulation["Company_Performance"]
        + company_change
    ).clip(
        lower=50,
        upper=100
    )


    # --------------------------------------------------------
    # OVERALL PERFORMANCE SCORE
    # --------------------------------------------------------

    simulation["Simulated_Overall_Score"] = (
        simulation["Individual_Performance"] * 0.40
        + simulation["Goal_Achievement_Normalized"] * 0.30
        + simulation["Competency_Score"] * 0.15
        + simulation["Simulated_Company_Performance"] * 0.15
    ).round(2)


    # --------------------------------------------------------
    # PAYOUT MULTIPLIER
    # --------------------------------------------------------

    simulation["Simulated_Payout_Multiplier"] = (
        simulation["Simulated_Overall_Score"]
        .apply(calculate_payout_multiplier)
    )


    # --------------------------------------------------------
    # TARGET VARIABLE PAY ADJUSTMENT
    # --------------------------------------------------------

    target_change = (
        target_variable_pay
        - df["Target_Variable_Pay_Pct"].mean()
    )

    simulation["Simulated_Target_Variable_Pay_Pct"] = (
        simulation["Target_Variable_Pay_Pct"]
        + target_change
    ).clip(lower=0)


    # --------------------------------------------------------
    # TARGET VARIABLE PAY
    # --------------------------------------------------------

    simulation["Simulated_Target_Variable_Pay"] = (
        simulation["Base_Salary"]
        * simulation["Simulated_Target_Variable_Pay_Pct"]
    )


    # --------------------------------------------------------
    # PERFORMANCE THRESHOLD
    # --------------------------------------------------------

    simulation.loc[
        simulation["Simulated_Overall_Score"]
        < selected_threshold,
        "Simulated_Payout_Multiplier"
    ] = 0


    # --------------------------------------------------------
    # MAXIMUM PAYOUT CAP
    # --------------------------------------------------------

    simulation["Final_Payout_Multiplier"] = (
        simulation["Simulated_Payout_Multiplier"]
        .clip(
            upper=selected_max_payout
        )
    )


    # --------------------------------------------------------
    # FINAL VARIABLE PAY
    # --------------------------------------------------------

    simulation["Final_Variable_Pay"] = (
        simulation["Simulated_Target_Variable_Pay"]
        * simulation["Final_Payout_Multiplier"]
        * simulation["Department_Factor"]
    ).round(2)


    # --------------------------------------------------------
    # FINAL ELIGIBILITY
    # --------------------------------------------------------

    simulation.loc[
        simulation["Simulated_Overall_Score"]
        < selected_threshold,
        "Final_Variable_Pay"
    ] = 0


    # --------------------------------------------------------
    # TOTAL COMPENSATION
    # --------------------------------------------------------

    simulation["Final_Total_Compensation"] = (
        simulation["Base_Salary"]
        + simulation["Final_Variable_Pay"]
    ).round(2)


    # --------------------------------------------------------
    # VARIABLE PAY AS % OF SALARY
    # --------------------------------------------------------

    simulation["Final_Variable_Pay_Pct"] = (
        simulation["Final_Variable_Pay"]
        / simulation["Base_Salary"]
        * 100
    ).round(2)


    # --------------------------------------------------------
    # GOVERNANCE STATUS
    # --------------------------------------------------------

    simulation["Final_Governance_Status"] = np.where(

        simulation["Simulated_Overall_Score"]
        < selected_threshold,

        "Below Threshold",

        np.where(

            simulation["Final_Payout_Multiplier"]
            >= selected_max_payout,

            "Maximum Payout",

            "Within Policy"
        )
    )


    return simulation


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("Variable Pay Simulation Model")

st.markdown(
    """
    **HR Compensation Planning & Decision Support Tool**

    Simulate employee-level variable pay outcomes for a
    synthetic workforce of 500 employees under different
    compensation and performance assumptions.
    """
)

st.divider()


# ============================================================
# SIMULATION CONTROLS
# ============================================================

st.subheader("Simulation Controls")

col1, col2, col3 = st.columns(3)

with col1:

    company_performance = st.slider(
        "Company Performance (%)",
        min_value=0,
        max_value=100,
        value=50
        step=1
    )


with col2:

    target_variable_pay = st.slider(
        "Target Variable Pay (%)",
        min_value=5,
        max_value=25,
        value=5
        step=1
    )


with col3:

    selected_budget = st.number_input(
        "Variable Pay Budget (₹)",
        min_value=1_000_000,
        max_value=100_000_000,
        value=30_000_000,
        step=100_000
    )


col4, col5 = st.columns(2)

with col4:

    selected_threshold = st.slider(
        "Minimum Performance Threshold",
        min_value=40,
        max_value=80,
        value=40,
        step=1
    )


with col5:

    selected_max_payout = st.slider(
        "Maximum Payout (% of Target)",
        min_value=50,
        max_value=150,
        value=10,
        step=5
    ) / 100


# ============================================================
# RUN SIMULATION
# ============================================================

st.divider()

run_simulation = st.button(
    "RUN VARIABLE PAY SIMULATION",
    type="primary",
    use_container_width=True
)


if run_simulation:

    simulation = generate_final_simulation(
        company_performance=company_performance,
        target_variable_pay=target_variable_pay / 100,
        selected_budget=selected_budget,
        selected_threshold=selected_threshold,
        selected_max_payout=selected_max_payout
    )
    st.session_state.simulation = simulation
    st.session_state.simulation_run = True


if st.session_state.simulation_run:

    simulation = st.session_state.simulation

    


    # ========================================================
    # KEY METRICS
    # ========================================================

    total_variable_pay = (
        simulation["Final_Variable_Pay"].sum()
    )

    average_variable_pay = (
        simulation["Final_Variable_Pay"].mean()
    )

    average_performance = (
        simulation["Simulated_Overall_Score"].mean()
    )

    employees_receiving_payout = (
        simulation["Final_Variable_Pay"] > 0
    ).sum()

    budget_utilization = (
        total_variable_pay
        / selected_budget
        * 100
    )


    if total_variable_pay <= selected_budget:
        budget_status = "WITHIN BUDGET"
    else:
        budget_status = "OVER BUDGET"


    # ========================================================
    # KPI DISPLAY
    # ========================================================

    st.subheader("Simulation Results")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    kpi1.metric(
        "Total Variable Pay",
        f"₹{total_variable_pay:,.0f}"
    )

    kpi2.metric(
        "Budget Utilization",
        f"{budget_utilization:.1f}%"
    )

    kpi3.metric(
        "Average Performance",
        f"{average_performance:.2f}"
    )

    kpi4.metric(
        "Employees Receiving Payout",
        f"{employees_receiving_payout}"
    )

    kpi5.metric(
        "Budget Status",
        budget_status
    )


    # ========================================================
    # DEPARTMENT ANALYSIS
    # ========================================================

    st.divider()

    st.subheader("Variable Pay by Department")

    department_summary = (
        simulation
        .groupby("Department")
        .agg(
            Employees=("Employee_ID", "count"),
            Total_Variable_Pay=(
                "Final_Variable_Pay",
                "sum"
            ),
            Average_Variable_Pay=(
                "Final_Variable_Pay",
                "mean"
            ),
            Average_Performance=(
                "Simulated_Overall_Score",
                "mean"
            )
        )
        .reset_index()
        .sort_values(
            "Total_Variable_Pay",
            ascending=False
        )
    )

    st.bar_chart(
        department_summary.set_index(
            "Department"
        )["Total_Variable_Pay"]
    )


    # ========================================================
    # PERFORMANCE VS PAYOUT
    # ========================================================

    st.subheader("Performance vs Variable Pay")

    performance_chart = simulation[
        [
            "Simulated_Overall_Score",
            "Final_Variable_Pay"
        ]
    ].rename(
        columns={
            "Simulated_Overall_Score":
                "Performance Score",
            "Final_Variable_Pay":
                "Variable Pay"
        }
    )

    st.scatter_chart(
        performance_chart,
        x="Performance Score",
        y="Variable Pay"
    )


    # ========================================================
    # EMPLOYEE PAYOUT REGISTER
    # ========================================================

    st.divider()

    st.subheader("Employee-Level Payout Register")

    employee_output = simulation[
        [
            "Employee_ID",
            "Department",
            "Job_Level",
            "Base_Salary",
            "Target_Variable_Pay_Pct",
            "Simulated_Overall_Score",
            "Final_Payout_Multiplier",
            "Simulated_Target_Variable_Pay",
            "Final_Variable_Pay",
            "Final_Variable_Pay_Pct",
            "Final_Total_Compensation",
            "Final_Governance_Status"
        ]
    ].copy()

    employee_output = employee_output.sort_values(
        "Final_Variable_Pay",
        ascending=False
    )

    st.dataframe(
        employee_output,
        use_container_width=True,
        height=500
    )


    # ========================================================
    # DOWNLOAD RESULTS
    # ========================================================

    csv_data = employee_output.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Employee Payout Register",
        data=csv_data,
        file_name="variable_pay_payout_register.csv",
        mime="text/csv",
        use_container_width=True
    )
        # ========================================================
    # SCENARIO ANALYSIS
    # ========================================================

    st.divider()

    st.subheader("Scenario Analysis")

    st.markdown(
        """
        Compare the impact of alternative compensation and
        company-performance assumptions on total variable-pay cost.
        """
    )

    scenario_definitions = {
        "Base Case": {
            "company_performance": 82,
            "target_variable_pay": 12
        },

        "Upside Case": {
            "company_performance": 95,
            "target_variable_pay": 12
        },

        "Downside Case": {
            "company_performance": 70,
            "target_variable_pay": 12
        },

        "High Incentive Case": {
            "company_performance": 82,
            "target_variable_pay": 15
        }
    }


    scenario_results = []

    for scenario_name, assumptions in scenario_definitions.items():

        scenario_simulation = generate_final_simulation(

            company_performance=(
                assumptions["company_performance"]
            ),

            target_variable_pay=(
                assumptions["target_variable_pay"] / 100
            ),

            selected_budget=selected_budget,

            selected_threshold=selected_threshold,

            selected_max_payout=selected_max_payout
        )


        scenario_total_variable_pay = (
            scenario_simulation[
                "Final_Variable_Pay"
            ].sum()
        )


        scenario_average_payout = (
            scenario_simulation[
                "Final_Variable_Pay"
            ].mean()
        )


        scenario_employees_paid = (
            scenario_simulation[
                "Final_Variable_Pay"
            ] > 0
        ).sum()


        scenario_budget_utilization = (
            scenario_total_variable_pay
            / selected_budget
            * 100
        )


        if scenario_total_variable_pay <= selected_budget:
            scenario_budget_status = "Within Budget"
        else:
            scenario_budget_status = "Over Budget"


        scenario_results.append({

            "Scenario": scenario_name,

            "Company Performance (%)":
                assumptions["company_performance"],

            "Target Variable Pay (%)":
                assumptions["target_variable_pay"],

            "Total Variable Pay":
                scenario_total_variable_pay,

            "Average Payout":
                scenario_average_payout,

            "Employees Receiving Payout":
                scenario_employees_paid,

            "Budget Utilization (%)":
                scenario_budget_utilization,

            "Budget Status":
                scenario_budget_status
        })


    scenario_comparison = pd.DataFrame(
        scenario_results
    )


    # ========================================================
    # SCENARIO TABLE
    # ========================================================

    st.dataframe(
        scenario_comparison.style.format({

            "Total Variable Pay":
                "₹{:,.0f}",

            "Average Payout":
                "₹{:,.0f}",

            "Budget Utilization (%)":
                "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # SCENARIO COST CHART
    # ========================================================

    st.subheader("Variable Pay Cost by Scenario")

    scenario_chart_data = scenario_comparison[
        [
            "Scenario",
            "Total Variable Pay"
        ]
    ].set_index("Scenario")


    st.bar_chart(
        scenario_chart_data
    )


    # ========================================================
    # SCENARIO BUDGET COMPARISON
    # ========================================================

    st.subheader("Scenario Budget Utilization")

    budget_chart_data = scenario_comparison[
        [
            "Scenario",
            "Budget Utilization (%)"
        ]
    ].set_index("Scenario")


    st.bar_chart(
        budget_chart_data
    )
        # ========================================================
    # EMPLOYEE EXPLORER
    # ========================================================

    st.divider()

    st.subheader("Employee Explorer")

    st.markdown(
        """
        Select an employee to examine the drivers behind
        their simulated variable-pay outcome.
        """
    )

    employee_list = simulation[
        "Employee_ID"
    ].tolist()

    selected_employee_id = st.selectbox(
        "Select Employee",
        employee_list
    )

    selected_employee = simulation[
        simulation["Employee_ID"]
        == selected_employee_id
    ].iloc[0]


    # ========================================================
    # EMPLOYEE PROFILE
    # ========================================================

    st.markdown("### Employee Profile")

    profile_col1, profile_col2, profile_col3 = st.columns(3)

    with profile_col1:

        st.write(
            f"**Employee ID:** "
            f"{selected_employee['Employee_ID']}"
        )

        st.write(
            f"**Department:** "
            f"{selected_employee['Department']}"
        )

        st.write(
            f"**Job Level:** "
            f"{selected_employee['Job_Level']}"
        )


    with profile_col2:

        st.write(
            f"**Base Salary:** "
            f"₹{selected_employee['Base_Salary']:,.0f}"
        )

        st.write(
            f"**Target Variable Pay:** "
            f"{selected_employee['Target_Variable_Pay_Pct'] * 100:.1f}%"
        )

        st.write(
            f"**Department Factor:** "
            f"{selected_employee['Department_Factor']:.2f}x"
        )


    with profile_col3:

        st.write(
            f"**Final Variable Pay:** "
            f"₹{selected_employee['Final_Variable_Pay']:,.0f}"
        )

        st.write(
            f"**Total Compensation:** "
            f"₹{selected_employee['Final_Total_Compensation']:,.0f}"
        )

        st.write(
            f"**Governance Status:** "
            f"{selected_employee['Final_Governance_Status']}"
        )


    # ========================================================
    # PERFORMANCE BREAKDOWN
    # ========================================================

    st.markdown("### Performance Breakdown")

    performance_breakdown = pd.DataFrame({

        "Performance Component": [
            "Individual Performance",
            "Goal Achievement",
            "Competency Score",
            "Company Performance"
        ],

        "Score": [
            selected_employee[
                "Individual_Performance"
            ],

            selected_employee[
                "Goal_Achievement_Normalized"
            ],

            selected_employee[
                "Competency_Score"
            ],

            selected_employee[
                "Simulated_Company_Performance"
            ]
        ],

        "Weight": [
            "40%",
            "30%",
            "15%",
            "15%"
        ]
    })

    st.dataframe(
        performance_breakdown,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # PAYOUT CALCULATION
    # ========================================================

    st.markdown("### Payout Calculation")

    payout_col1, payout_col2, payout_col3 = st.columns(3)

    with payout_col1:

        st.metric(
            "Overall Performance Score",
            f"{selected_employee['Simulated_Overall_Score']:.2f}"
        )


    with payout_col2:

        st.metric(
            "Payout Multiplier",
            f"{selected_employee['Final_Payout_Multiplier']:.2f}x"
        )


    with payout_col3:

        st.metric(
            "Final Variable Pay",
            f"₹{selected_employee['Final_Variable_Pay']:,.0f}"
        )


    # ========================================================
    # CALCULATION TRACE
    # ========================================================

    st.markdown("### Calculation Trace")

    st.code(
        f"""
Base Salary
₹{selected_employee['Base_Salary']:,.2f}

× Target Variable Pay
{selected_employee['Target_Variable_Pay_Pct'] * 100:.2f}%

= Target Variable Pay
₹{selected_employee['Simulated_Target_Variable_Pay']:,.2f}

× Payout Multiplier
{selected_employee['Final_Payout_Multiplier']:.2f}x

× Department Factor
{selected_employee['Department_Factor']:.2f}x

= Final Variable Pay
₹{selected_employee['Final_Variable_Pay']:,.2f}
        """,
        language="text"
    )
# ============================================================
# BUDGET & GOVERNANCE DASHBOARD
# ============================================================


if st.session_state.simulation_run:

    simulation = st.session_state.simulation

    st.divider()

    st.subheader("Budget & Governance Dashboard")

    st.markdown(
        """
        Assess whether the simulated variable-pay pool remains
        within the approved budget and compensation governance rules.
        """
    )

    # ------------------------------------------------------------
    # BUDGET METRICS
    # ------------------------------------------------------------

    approved_budget = selected_budget

    actual_variable_pay = (
        simulation["Final_Variable_Pay"].sum()
    )

    budget_surplus_deficit = (
        approved_budget - actual_variable_pay
    )

    budget_utilization = (
        actual_variable_pay
        / approved_budget
        * 100
    )

    employees_below_threshold = (
        simulation["Simulated_Overall_Score"]
        < selected_threshold
    ).sum()

    employees_at_maximum_payout = (
        simulation["Final_Payout_Multiplier"]
        >= selected_max_payout
    ).sum()

    employees_within_policy = (
        simulation["Final_Governance_Status"]
        == "Within Policy"
    ).sum()


# ------------------------------------------------------------
# GOVERNANCE STATUS
# ------------------------------------------------------------

    if budget_surplus_deficit >= 0:

        overall_budget_status = "WITHIN APPROVED BUDGET"

    else:

        overall_budget_status = "BUDGET EXCEEDED"


# ------------------------------------------------------------
# KPI DISPLAY
# ------------------------------------------------------------

    budget_col1, budget_col2, budget_col3 = st.columns(3)

    with budget_col1:

        st.metric(
            "Approved Budget",
            f"₹{approved_budget:,.0f}"
        )

    with budget_col2:

        st.metric(
            "Simulated Variable Pay",
            f"₹{actual_variable_pay:,.0f}"
        )

    with budget_col3:

        st.metric(
            "Budget Utilization",
            f"{budget_utilization:.1f}%"
        )


    budget_col4, budget_col5, budget_col6 = st.columns(3)

    with budget_col4:

        st.metric(
            "Budget Surplus / Deficit",
            f"₹{budget_surplus_deficit:,.0f}"
        )

    with budget_col5:

        st.metric(
            "Below Threshold",
            f"{employees_below_threshold}"
        )

    with budget_col6:

        st.metric(
            "At Maximum Payout",
            f"{employees_at_maximum_payout}"
        )


# ------------------------------------------------------------
# OVERALL STATUS
# ------------------------------------------------------------

    if overall_budget_status == "WITHIN APPROVED BUDGET":

        st.success(
            f"✓ {overall_budget_status}"
        )

    else:

        st.error(
            f"⚠ {overall_budget_status}"
        )
   
    # --------------------------------------------------------
    # GOVERNANCE DISTRIBUTION
    # --------------------------------------------------------

    st.markdown("### Governance Distribution")

    governance_summary = (
        simulation["Final_Governance_Status"]
        .value_counts()
        .reset_index()
    )

    governance_summary.columns = [
        "Governance Status",
        "Employees"
    ]

    st.dataframe(
        governance_summary,
        use_container_width=True,
        hide_index=True
    )


    # ============================================================
    # PAYOUT CONCENTRATION BY DEPARTMENT
    # ============================================================

    st.markdown("### Variable Pay Concentration by Department")

    department_payout = (
        simulation.groupby("Department")["Final_Variable_Pay"]
        .sum()
        .reset_index()
        .sort_values(
            "Final_Variable_Pay",
            ascending=False
        )
    )

    department_payout["Payout Share (%)"] = (
        department_payout["Final_Variable_Pay"]
        / actual_variable_pay
        * 100
    )

    st.dataframe(
        department_payout.style.format({
            "Final_Variable_Pay": "₹{:,.0f}",
            "Payout Share (%)": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# BUDGET OPTIMIZATION & POLICY RECOMMENDATION
# ============================================================

st.divider()

st.subheader("Budget Optimization & Policy Recommendation")

st.markdown(
    """
    This analysis evaluates alternative compensation-policy settings
    against the approved variable-pay budget. The current simulation
    remains unchanged; these are alternative policy tests.
    """
)

# ============================================================
# BASELINE
# ============================================================

baseline_simulation = st.session_state.get("simulation")

if baseline_simulation is not None:

    baseline_payout = (
        baseline_simulation["Final_Variable_Pay"].sum()
    )

    baseline_budget_gap = (
        selected_budget - baseline_payout
    )

    baseline_reduction_required = (
        max(
            0,
            (baseline_payout - selected_budget)
            / baseline_payout
            * 100
        )
    )

# ------------------------------------------------------------
# DEFINE POLICY OPTIONS
# ------------------------------------------------------------

# Test target variable-pay levels from 5% to the
# currently selected target percentage.

target_options = [
    value / 100
    for value in range(
        5,
        int(target_variable_pay) + 1
    )
]


# Test progressively stronger performance thresholds.

threshold_options = [
    50,
    55,
    60,
    65,
    70,
    75,
    80,
    85
]


# Test different maximum payout caps.

maximum_payout_options = [
    0.50,
    0.75,
    1.00,
    1.25,
    1.50
]



# ------------------------------------------------------------
# TEST ALTERNATIVE POLICIES
# ------------------------------------------------------------

optimization_results = []

for target_option in target_options:

    for threshold_option in threshold_options:

        for max_payout_option in maximum_payout_options:

            policy_simulation = generate_final_simulation(

                company_performance=company_performance,

                target_variable_pay=target_option,

                selected_budget=selected_budget,

                selected_threshold=threshold_option,

                selected_max_payout=max_payout_option
            )

            projected_payout = (
                policy_simulation[
                    "Final_Variable_Pay"
                ].sum()
            )

            budget_gap = (
                selected_budget - projected_payout
            )

            budget_utilization = (
                projected_payout
                / selected_budget
                * 100
            )

            employees_receiving_payout = (
                policy_simulation[
                    "Final_Variable_Pay"
                ] > 0
            ).sum()

            optimization_results.append({

                "Target Variable Pay (%)":
                    target_option * 100,

                "Minimum Performance Threshold":
                    threshold_option,

                "Maximum Payout (%)":
                    max_payout_option * 100,

                "Projected Variable Pay":
                    projected_payout,

                "Budget Gap":
                    budget_gap,

                "Budget Utilization (%)":
                    budget_utilization,

                "Employees Receiving Payout":
                    employees_receiving_payout
            })


optimization_df = pd.DataFrame(
    optimization_results
)

# ------------------------------------------------------------
# IDENTIFY BEST POLICY
# ------------------------------------------------------------

feasible_options = optimization_df[
    optimization_df["Budget Gap"] >= 0
].copy()

if not feasible_options.empty:

    recommended_policy = (
        feasible_options
        .sort_values(
            "Budget Gap",
            ascending=True
        )
        .iloc[0]
    )

    recommendation_status = (
        "RECOMMENDED POLICY — WITHIN BUDGET"
    )

else:

    recommended_policy = (
        optimization_df
        .sort_values(
            "Projected Variable Pay",
            ascending=True
        )
        .iloc[0]
    )

    recommendation_status = (
        "NO TESTED POLICY FITS THE BUDGET"
    )

# ------------------------------------------------------------
# RECOMMENDATION DISPLAY
# ------------------------------------------------------------

if feasible_options.empty:

    st.warning(
        "No tested policy combination brings the "
        "projected variable-pay cost within the approved budget."
    )

else:

    st.success(
        recommendation_status
    )


# ------------------------------------------------------------
# RECOMMENDED POLICY METRICS
# ------------------------------------------------------------

rec_col1, rec_col2, rec_col3 = st.columns(3)

with rec_col1:

    st.metric(
        "Recommended Target Variable Pay",
        f"{recommended_policy['Target Variable Pay (%)']:.1f}%"
    )

with rec_col2:

    st.metric(
        "Recommended Threshold",
        f"{recommended_policy['Minimum Performance Threshold']:.0f}"
    )

with rec_col3:

    st.metric(
        "Recommended Maximum Payout",
        f"{recommended_policy['Maximum Payout (%)']:.0f}%"
    )


rec_col4, rec_col5, rec_col6 = st.columns(3)

with rec_col4:

    st.metric(
        "Projected Variable Pay",
        f"₹{recommended_policy['Projected Variable Pay']:,.0f}"
    )

with rec_col5:

    st.metric(
        "Budget Utilization",
        f"{recommended_policy['Budget Utilization (%)']:.1f}%"
    )

with rec_col6:

    st.metric(
        "Projected Budget Gap",
        f"₹{recommended_policy['Budget Gap']:,.0f}"
    )


# ============================================================
# BASELINE PAYOUT
# ============================================================

if st.session_state.simulation_run:
    simulation = st.session_state.simulation

    baseline_payout = simulation["Final_Variable_Pay"].sum()

    baseline_budget_gap = (
        selected_budget - baseline_payout
    )

    baseline_reduction_required = (
        max(
            0,
            (baseline_payout - selected_budget)
            / baseline_payout
            * 100
        )
    )
# ============================================================
# BASELINE VS RECOMMENDED
# ============================================================

    st.markdown("### Baseline vs Recommended Policy")

    comparison_df = pd.DataFrame({

        "Metric": [
            "Target Variable Pay (%)",
            "Minimum Performance Threshold",
            "Maximum Payout (%)",
            "Projected Variable Pay",
            "Budget Utilization (%)"
        ],

        "Current Policy": [
            target_variable_pay,
            selected_threshold,
            selected_max_payout * 100,
            baseline_payout,
            baseline_payout / selected_budget * 100
        ],

        "Recommended Policy": [
            recommended_policy[
                "Target Variable Pay (%)"
            ],

            recommended_policy[
                "Minimum Performance Threshold"
            ],

            recommended_policy[
                "Maximum Payout (%)"
            ],

            recommended_policy[
                "Projected Variable Pay"
            ],

            recommended_policy[
                "Budget Utilization (%)"
            ]
        ]
    })

    st.dataframe(
        comparison_df.style.format({
            "Current Policy": "{:,.2f}",
            "Recommended Policy": "{:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# POLICY OPTIONS
# ------------------------------------------------------------

st.markdown("### Tested Policy Alternatives")

display_optimization = optimization_df.sort_values(
    "Budget Gap",
    ascending=False
).copy()

st.dataframe(
    display_optimization.style.format({

        "Target Variable Pay (%)":
            "{:.1f}%",

        "Maximum Payout (%)":
            "{:.0f}%",

        "Projected Variable Pay":
            "₹{:,.0f}",

        "Budget Gap":
            "₹{:,.0f}",

        "Budget Utilization (%)":
            "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)
# ============================================================
# EXECUTIVE MANAGEMENT DASHBOARD
# ============================================================

if st.session_state.simulation_run:

    st.divider()

    st.subheader("Executive Decision Summary")

    st.markdown(
        """
        Management-level view of the current variable-pay policy,
        financial impact, and model-generated policy recommendation.
        """
    )

    # --------------------------------------------------------
    # CURRENT POLICY METRICS
    # --------------------------------------------------------

    current_policy_cost = (
        simulation["Final_Variable_Pay"].sum()
    )

    current_budget = selected_budget

    current_budget_utilization = (
        current_policy_cost
        / current_budget
        * 100
    )

    current_budget_gap = (
        current_budget
        - current_policy_cost
    )

    # --------------------------------------------------------
    # RECOMMENDED POLICY METRICS
    # --------------------------------------------------------

    recommended_policy_cost = (
        recommended_policy[
            "Projected Variable Pay"
        ]
    )

    recommended_budget_utilization = (
        recommended_policy[
            "Budget Utilization (%)"
        ]
    )

    projected_savings = (
        current_policy_cost
        - recommended_policy_cost
    )

    # --------------------------------------------------------
    # TOP-LEVEL KPIs
    # --------------------------------------------------------

    exec_col1, exec_col2, exec_col3 = st.columns(3)

    with exec_col1:

        st.metric(
            "Current Policy Cost",
            f"₹{current_policy_cost:,.0f}"
        )

    with exec_col2:

        st.metric(
            "Approved Budget",
            f"₹{current_budget:,.0f}"
        )

    with exec_col3:

        st.metric(
            "Current Budget Utilization",
            f"{current_budget_utilization:.1f}%"
        )


    exec_col4, exec_col5, exec_col6 = st.columns(3)

    with exec_col4:

        st.metric(
            "Recommended Policy Cost",
            f"₹{recommended_policy_cost:,.0f}"
        )

    with exec_col5:

        st.metric(
            "Projected Savings",
            f"₹{projected_savings:,.0f}"
        )

    with exec_col6:

        st.metric(
            "Recommended Utilization",
            f"{recommended_budget_utilization:.1f}%"
        )


    # --------------------------------------------------------
    # CURRENT POLICY
    # --------------------------------------------------------

    st.markdown("### Current Policy")

    current_policy_summary = pd.DataFrame({

        "Policy Lever": [
            "Target Variable Pay",
            "Minimum Performance Threshold",
            "Maximum Payout"
        ],

        "Current Setting": [
            f"{target_variable_pay:.1f}%",
            f"{selected_threshold}",
            f"{selected_max_payout * 100:.0f}%"
        ]
    })

    st.dataframe(
        current_policy_summary,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # RECOMMENDED POLICY
    # --------------------------------------------------------

    st.markdown("### Model-Recommended Policy")

    recommended_policy_summary = pd.DataFrame({

        "Policy Lever": [
            "Target Variable Pay",
            "Minimum Performance Threshold",
            "Maximum Payout"
        ],

        "Recommended Setting": [

            f"{recommended_policy['Target Variable Pay (%)']:.1f}%",

            f"{recommended_policy['Minimum Performance Threshold']:.0f}",

            f"{recommended_policy['Maximum Payout (%)']:.0f}%"
        ]
    })

    st.dataframe(
        recommended_policy_summary,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # DECISION STATUS
    # --------------------------------------------------------

    if recommended_policy_cost <= current_budget:

        st.success(
            "RECOMMENDATION: The model-generated policy "
            "configuration fits within the approved budget."
        )

    else:

        st.warning(
            "RECOMMENDATION: The tested policy options "
            "do not currently fit within the approved budget."
        )


    # --------------------------------------------------------
    # BUDGET IMPACT
    # --------------------------------------------------------

    st.markdown("### Financial Impact")

    impact_df = pd.DataFrame({

        "Metric": [
            "Current Policy Cost",
            "Recommended Policy Cost",
            "Approved Budget",
            "Projected Savings",
            "Current Budget Utilization",
            "Recommended Budget Utilization"
        ],

        "Value": [

            current_policy_cost,

            recommended_policy_cost,

            current_budget,

            projected_savings,

            current_budget_utilization,

            recommended_budget_utilization
        ]
    })

    st.dataframe(
        impact_df.style.format({
            "Value": "₹{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # MANAGEMENT INTERPRETATION
    # --------------------------------------------------------

    st.markdown("### Management Interpretation")

    if projected_savings > 0:

        st.write(
            f"""
            The current policy produces an estimated variable-pay
            cost of ₹{current_policy_cost:,.0f}, compared with an
            approved budget of ₹{current_budget:,.0f}.

            The model-tested recommended policy reduces projected
            variable-pay cost to ₹{recommended_policy_cost:,.0f},
            creating an estimated budget improvement of
            ₹{projected_savings:,.0f}.

            The recommended configuration uses a target variable-pay
            level of {recommended_policy['Target Variable Pay (%)']:.1f}%,
            a minimum performance threshold of
            {recommended_policy['Minimum Performance Threshold']:.0f},
            and a maximum payout of
            {recommended_policy['Maximum Payout (%)']:.0f}%.
            """
        )

    else:

        st.write(
            """
            The current policy does not produce a lower projected
            cost than the model-tested recommendation. Further
            policy testing may therefore be required.
            """
        )
        # ============================================================
# ABOUT THIS MODEL
# ============================================================

st.divider()

st.subheader("About This Model")

st.markdown("""
### Purpose

This Variable Pay Simulation Model is designed to evaluate how different
performance-based compensation policies may affect employee payouts and the
organization's overall variable-pay budget.

The model helps management compare alternative compensation policies,
evaluate budget utilization, and identify a policy that balances employee
performance rewards with compensation governance.

### Synthetic Data Disclaimer

This model uses a **synthetic workforce of 500 employees** created for
academic and analytical purposes.

The employee records, performance scores, compensation values, departmental
data, and simulated payouts do **not represent real employees or actual
company payroll data**.

Therefore, the results should be interpreted as a **simulation of possible
compensation outcomes**, rather than as actual compensation recommendations
for a real organization.

### Performance Weighting

Employee performance is incorporated into the variable-pay calculation
through the overall performance score.

Higher performance scores result in higher potential variable-pay outcomes,
subject to the defined performance thresholds and maximum payout limits.

This creates a performance-linked compensation structure in which variable
pay increases as employee performance improves.

### Payout Logic

The model calculates variable pay using the employee's eligible compensation,
performance outcome, and the selected variable-pay policy.

The payout is constrained by the selected maximum payout percentage and
performance threshold.

This ensures that the model does not provide unlimited variable-pay
payouts and maintains consistency with the defined compensation policy.

### Governance Rules

The model incorporates governance controls to ensure that simulated payouts
remain aligned with the approved variable-pay budget.

Key governance checks include:

- Approved variable-pay budget
- Budget utilization
- Budget surplus or deficit
- Performance threshold
- Maximum payout limit
- Overall budget status

A policy is considered acceptable when the projected payout remains within
the approved compensation budget.

### Optimization Logic

The optimization component evaluates alternative combinations of:

- Target variable pay percentage
- Minimum performance threshold
- Maximum payout percentage

Each policy alternative is tested against the approved budget.

The model compares projected variable-pay expenditure and budget utilization
to identify a policy that provides an appropriate balance between
performance-based rewards and financial control.

The recommended policy is therefore generated from the simulated policy
scenarios rather than being treated as a fixed or universal compensation
rule.
""")
# ============================================================
# EXPORTABLE MANAGEMENT REPORT
# PDF + EXCEL DOWNLOAD
# ============================================================

if st.session_state.simulation_run:

    st.divider()

    st.subheader("Management Report")

    # --------------------------------------------------------
    # REPORT CALCULATIONS
    # --------------------------------------------------------

    report_baseline_payout = pd.to_numeric(
        st.session_state.simulation["Final_Variable_Pay"],
        errors="coerce"
    ).sum()

    report_budget_utilization = (
        report_baseline_payout / selected_budget * 100
        if selected_budget > 0
        else 0
    )

    report_budget_gap = (
        selected_budget - report_baseline_payout
    )

    report_budget_status = (
        "WITHIN BUDGET"
        if report_baseline_payout <= selected_budget
        else "OVER BUDGET"
    )

    recommended_budget_utilization = (
        recommended_policy["Budget Utilization (%)"]
    )

    recommended_budget_status = (
        "WITHIN BUDGET"
        if recommended_budget_utilization <= 100
        else "OVER BUDGET"
    )

    # --------------------------------------------------------
    # MANAGEMENT REPORT TEXT
    # --------------------------------------------------------

    report_text = f"""
VARIABLE PAY MANAGEMENT REPORT
========================================

MODEL OVERVIEW
----------------------------------------

Workforce Size: 500 synthetic employees
Data Type: Synthetic / Academic Simulation

PURPOSE
----------------------------------------

This model simulates a variable-pay compensation system
using synthetic employee data. It evaluates employee
performance, applies the defined payout logic, compares
projected payouts with the approved budget, and tests
alternative compensation-policy settings.

BUDGET & PAYOUT SUMMARY
----------------------------------------

Approved Variable Pay Budget: INR {selected_budget:,.0f}
Current Projected Variable Pay: INR {report_baseline_payout:,.0f}
Current Budget Utilization: {report_budget_utilization:.1f}%
Current Budget Gap: INR {report_budget_gap:,.0f}
Current Budget Status: {report_budget_status}

RECOMMENDED POLICY
----------------------------------------

Target Variable Pay: {recommended_policy["Target Variable Pay (%)"]:.1f}%
Minimum Performance Threshold: {recommended_policy["Minimum Performance Threshold"]}
Maximum Payout: {recommended_policy["Maximum Payout (%)"]:.1f}%
Projected Variable Pay: INR {recommended_policy["Projected Variable Pay"]:,.0f}
Budget Utilization: {recommended_budget_utilization:.1f}%
Budget Status: {recommended_budget_status}

GOVERNANCE STATUS
----------------------------------------

The recommended policy is evaluated against the approved
variable-pay budget.

Policy Status: {recommended_budget_status}

POLICY OPTIMIZATION
----------------------------------------

The recommended policy was selected by testing alternative
combinations of target variable pay, minimum performance
threshold, and maximum payout against the approved
variable-pay budget.

The optimization process identifies a policy configuration
that maintains budget discipline while supporting the
variable-pay objectives of the simulated workforce.

POLICY INTERPRETATION
----------------------------------------

The simulation links employee performance outcomes with
variable-pay payouts. Higher performance can result in
higher payouts subject to the defined threshold and
maximum-payout rules.

The recommended policy represents the policy configuration
identified through the tested simulation alternatives and
budget constraints.

DATA DISCLAIMER
----------------------------------------

This model uses synthetic employee data created for
academic purposes.

No real employee compensation, salary, or performance
data is used.

The results should not be interpreted as an actual
compensation recommendation for a real organization.
"""

    # --------------------------------------------------------
    # DISPLAY MANAGEMENT REPORT
    # --------------------------------------------------------

    with st.expander("View Management Report", expanded=True):

        st.text(report_text)

    # ========================================================
    # PDF MANAGEMENT REPORT
    # ========================================================

    from io import BytesIO
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer
    )

    pdf_buffer = BytesIO()

    pdf_doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    # PDF TITLE
    story.append(
        Paragraph(
            "VARIABLE PAY MANAGEMENT REPORT",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # CONVERT REPORT TEXT INTO PDF
    for line in report_text.split("\n"):

        clean_line = line.strip()

        if clean_line == "":
            story.append(
                Spacer(1, 8)
            )

        elif clean_line.isupper():
            story.append(
                Paragraph(
                    f"<b>{escape(clean_line)}</b>",
                    styles["Heading2"]
                )
            )

            story.append(
                Spacer(1, 5)
            )

        else:
            story.append(
                Paragraph(
                    escape(clean_line),
                    styles["BodyText"]
                )
            )

            story.append(
                Spacer(1, 4)
            )

    pdf_doc.build(story)

    pdf_buffer.seek(0)

    # --------------------------------------------------------
    # EXCEL MANAGEMENT REPORT
    # --------------------------------------------------------

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        # --------------------------------------------
        # SUMMARY SHEET
        # --------------------------------------------

        summary_df = pd.DataFrame({
            "Metric": [
                "Workforce Size",
                "Data Type",
                "Approved Variable Pay Budget",
                "Current Projected Variable Pay",
                "Current Budget Utilization (%)",
                "Current Budget Gap",
                "Current Budget Status",
                "Recommended Target Variable Pay (%)",
                "Recommended Minimum Performance Threshold",
                "Recommended Maximum Payout (%)",
                "Recommended Projected Variable Pay",
                "Recommended Budget Utilization (%)",
                "Recommended Budget Status"
            ],

            "Value": [
                500,
                "Synthetic / Academic Simulation",
                selected_budget,
                report_baseline_payout,
                report_budget_utilization,
                report_budget_gap,
                report_budget_status,
                recommended_policy["Target Variable Pay (%)"],
                recommended_policy["Minimum Performance Threshold"],
                recommended_policy["Maximum Payout (%)"],
                recommended_policy["Projected Variable Pay"],
                recommended_budget_utilization,
                recommended_budget_status
            ]
        })

        summary_df.to_excel(
            writer,
            sheet_name="Management Summary",
            index=False
        )

        # --------------------------------------------
        # RECOMMENDED POLICY SHEET
        # --------------------------------------------

        policy_df = pd.DataFrame({
            "Policy Metric": [
                "Target Variable Pay (%)",
                "Minimum Performance Threshold",
                "Maximum Payout (%)",
                "Projected Variable Pay",
                "Budget Utilization (%)",
                "Budget Status"
            ],

            "Recommended Value": [
                recommended_policy["Target Variable Pay (%)"],
                recommended_policy["Minimum Performance Threshold"],
                recommended_policy["Maximum Payout (%)"],
                recommended_policy["Projected Variable Pay"],
                recommended_policy["Budget Utilization (%)"],
                recommended_budget_status
            ]
        })

        policy_df.to_excel(
            writer,
            sheet_name="Recommended Policy",
            index=False
        )

        # --------------------------------------------
        # POLICY ALTERNATIVES SHEET
        # --------------------------------------------

        if "policy_results" in locals():

            policy_results.to_excel(
                writer,
                sheet_name="Policy Alternatives",
                index=False
            )

        # --------------------------------------------
        # SIMULATION DATA SHEET
        # --------------------------------------------

        st.session_state.simulation.to_excel(
            writer,
            sheet_name="Simulation Data",
            index=False
        )

    excel_buffer.seek(0)

    # ========================================================
    # DOWNLOAD BUTTONS
    # ========================================================

    st.markdown("### Download Management Report")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name="Variable_Pay_Management_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col2:

        st.download_button(
            label="📊 Download Excel Report",
            data=excel_buffer,
            file_name="Variable_Pay_Management_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )