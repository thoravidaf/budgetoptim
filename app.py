import streamlit as st
import pulp
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Budget Optimization Dashboard", layout="wide")

st.title("📊 Marketing Budget Allocation Optimizer")
st.markdown("Adjust total budget and parameters in the sidebar to optimize conversions across channels.")

# --- SIDEBAR: INPUT PARAMETERS ---
st.sidebar.header("1. Total Budget Configuration")
total_budget = st.sidebar.number_input(
    "Total Available Budget ($)", 
    min_value=10000, 
    max_value=1000000, 
    value=100000, 
    step=5000
)

st.sidebar.header("2. Search Ads Constraint")
search_cap_pct = st.sidebar.slider(
    "Max Search Spend (% of Total Budget)", 
    min_value=10, 
    max_value=100, 
    value=50
) / 100.0

# --- OPTIMIZATION MODEL FUNCTION ---
def run_optimization(budget, search_cap):
    # Initialize the LP Problem
    prob = pulp.LpProblem("Budget_Optimization", pulp.LpMaximize)

    # Decision variables with bounds
    x_social = pulp.LpVariable("Social Media", lowBound=5000, upBound=budget * 0.5)
    x_search = pulp.LpVariable("Search Ads", lowBound=10000, upBound=budget * 0.6)
    x_tv     = pulp.LpVariable("TV Ads", lowBound=0, upBound=budget * 0.5)

    # Conversion Rates (Expected Return per dollar)
    roi_social, roi_search, roi_tv = 0.08, 0.12, 0.05

    # Objective Function
    prob += roi_social * x_social + roi_search * x_search + roi_tv * x_tv

    # Constraints
    prob += x_social + x_search + x_tv <= budget, "Total_Budget_Cap"
    prob += x_search <= search_cap * budget, "Search_Ads_Cap"

    # Solve without printing solver noise to console (msg=False)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    results = {
        "Social Media": x_social.varValue,
        "Search Ads": x_search.varValue,
        "TV Ads": x_tv.varValue
    }
    
    total_conversions = pulp.value(prob.objective)
    return results, total_conversions

# --- RUN MODEL & DISPLAY DASHBOARD ---
results_dict, max_conversions = run_optimization(total_budget, search_cap_pct)

df_results = pd.DataFrame(list(results_dict.items()), columns=["Channel", "Allocated Budget ($)"])
total_spent = df_results["Allocated Budget ($)"].sum()

# Top Metrics Display
col1, col2, col3 = st.columns(3)
col1.metric("Total Budget Allocated", f"${total_spent:,.2f}")
col2.metric("Remaining Unallocated", f"${total_budget - total_spent:,.2f}")
col3.metric("Expected Total Conversions", f"{max_conversions:,.2f}")

st.markdown("---")

# Visual Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Budget Allocation per Channel")
    fig_bar = px.bar(
        df_results, 
        x="Channel", 
        y="Allocated Budget ($)", 
        text_auto="$,.2f",
        color="Channel"
    )
    # Updated width syntax to fix Streamlit deprecation warning
    st.plotly_chart(fig_bar, width="stretch")

with col_chart2:
    st.subheader("Share of Wallet (%)")
    fig_pie = px.pie(
        df_results, 
        names="Channel", 
        values="Allocated Budget ($)", 
        hole=0.4
    )
    # Updated width syntax to fix Streamlit deprecation warning
    st.plotly_chart(fig_pie, width="stretch")