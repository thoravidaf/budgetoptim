import pulp

# 1. Initialize the Optimization Problem
problem = pulp.LpProblem("Budget_Allocation_Optimization", pulp.LpMaximize)

# 2. Define Decision Variables (Spending per channel in USD)
x_social = pulp.LpVariable("Social_Media_Spend", lowBound=5000, upBound=40000)
x_search = pulp.LpVariable("Search_Ads_Spend", lowBound=10000, upBound=60000)
x_tv     = pulp.LpVariable("TV_Ads_Spend", lowBound=0, upBound=50000)

# Expected Conversion Rates (Conversions per dollar spent)
rate_social = 0.08
rate_search = 0.12
rate_tv     = 0.05

# 3. Define Objective Function (Maximize total conversions)
problem += (
    rate_social * x_social + rate_search * x_search + rate_tv * x_tv,
    "Total_Conversions"
)

# 4. Define Constraints
total_budget = 100000

# Total spending cannot exceed the overall budget limit
problem += x_social + x_search + x_tv <= total_budget, "Max_Budget_Limit"

# Risk/Policy Constraint: Limit Search Ads to at most 50% of the budget
problem += x_search <= 0.50 * total_budget, "Max_Search_Cap"

# 5. Solve the Problem
problem.solve()

# 6. Display Results
print("=" * 40)
print(f"Status: {pulp.LpStatus[problem.status]}")
print("=" * 40)
print("Optimal Allocation Plan:")
print(f" • Social Media : ${x_social.varValue:,.2f}")
print(f" • Search Ads   : ${x_search.varValue:,.2f}")
print(f" • TV Ads       : ${x_tv.varValue:,.2f}")
print("-" * 40)
print(f"Total Budget Spent : ${x_social.varValue + x_search.varValue + x_tv.varValue:,.2f}")
print(f"Max expected conversions: {pulp.value(problem.objective):,.2f}")
print("=" * 40)