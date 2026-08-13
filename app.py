import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Variable Pay Simulation",
    page_icon="💼",
    layout="wide"
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
        min_value=50,
        max_value=100,
        value=82,
        step=1
    )


with col2:

    target_variable_pay = st.slider(
        "Target Variable Pay (%)",
        min_value=5,
        max_value=25,
        value=12,
        step=1
    )


with col3:

    selected_budget = st.number_input(
        "Variable Pay Budget (₹)",
        min_value=1_000_000,
        max_value=100_000_000,
        value=30_000_000,
        step=1_000_000
    )


col4, col5 = st.columns(2)

with col4:

    selected_threshold = st.slider(
        "Minimum Performance Threshold",
        min_value=40,
        max_value=80,
        value=50,
        step=5
    )


with col5:

    selected_max_payout = st.slider(
        "Maximum Payout (% of Target)",
        min_value=50,
        max_value=150,
        value=150,
        step=10
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