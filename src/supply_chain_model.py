"""
===========================================================
Supply Chain Network Optimization using Pyomo

This project develops a multi-period, multi-echelon supply
chain optimization model for Pars Dairy Company.

The model determines the optimal production, transportation,
and inventory decisions while minimizing the total supply
chain cost.

Author : Mohammad Amin Farhadi
University : Ferdowsi University of Mashhad
===========================================================
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

import pyomo.environ as pyo
import pandas as pd
import os


# ==========================================================
# Create Optimization Model
# ==========================================================

model = pyo.ConcreteModel()


# ==========================================================
# Read Input Data from Excel
# ==========================================================

# Load the Excel workbook
project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

data_path = os.path.join(
    project_root,
    "data",
    "supply_chain_data.xlsx"
)

data_file = pd.ExcelFile(data_path)

# Read factory information
factory_df = pd.read_excel(data_file, sheet_name="Factory")

# Read warehouse information
warehouse_df = pd.read_excel(data_file, sheet_name="Warehouse")

# Read market demand
market_df = pd.read_excel(data_file, sheet_name="Market")

# Read factory-to-warehouse distances
fw_distance_df = pd.read_excel(
    data_file,
    sheet_name="Factory_Warehouse_Distance",
    index_col=[0, 1]
)

# Read warehouse-to-market distances
wm_distance_df = pd.read_excel(
    data_file,
    sheet_name="Warehouse_Market_Distance",
    index_col=[0, 1]
)

# Read initial inventory
inventory_df = pd.read_excel(
    data_file,
    sheet_name="Initial_Inventory"
)

# Read global model parameters
parameters_df = pd.read_excel(
    data_file,
    sheet_name="Parameters"
)


# ==========================================================
# Sets
# ==========================================================

# Manufacturing plants
model.factory = pyo.Set(
    initialize=factory_df["Factory"].tolist()
)

# Distribution centers
model.warehouse = pyo.Set(
    initialize=warehouse_df["Warehouse"].tolist()
)

# Customer markets
model.market = pyo.Set(
    initialize=market_df["Market"].tolist()
)

# Planning periods
model.time = pyo.Set(
    initialize=["Jan", "Feb", "Mar", "Apr"]
)


# ==========================================================
# Parameters
# ==========================================================

# ---------- Factory Parameters ----------

production_capacity = factory_df.set_index(
    "Factory"
)["Capacity (Ton/Month)"].to_dict()

production_cost = factory_df.set_index(
    "Factory"
)["Production Cost (Toman/Ton)"].to_dict()

model.production_capacity = pyo.Param(
    model.factory,
    initialize=production_capacity
)

model.production_cost = pyo.Param(
    model.factory,
    initialize=production_cost
)


# ---------- Warehouse Parameters ----------

warehouse_capacity = warehouse_df.set_index(
    "Warehouse"
)["Capacity (Ton)"].to_dict()

inventory_holding_cost = warehouse_df.set_index(
    "Warehouse"
)["Holding Cost (Toman/Ton/Month)"].to_dict()

model.warehouse_capacity = pyo.Param(
    model.warehouse,
    initialize=warehouse_capacity
)

model.inventory_holding_cost = pyo.Param(
    model.warehouse,
    initialize=inventory_holding_cost
)


# ---------- Market Parameters ----------

market_demand = (
    market_df
    .set_index("Market")
    .stack()
    .to_dict()
)

model.market_demand = pyo.Param(
    model.market,
    model.time,
    initialize=market_demand
)


# ---------- Transportation Parameters ----------

factory_warehouse_distance = fw_distance_df[
    "Distance (km)"
]

model.factory_to_warehouse_distance = pyo.Param(
    model.factory,
    model.warehouse,
    initialize=factory_warehouse_distance
)

warehouse_market_distance = wm_distance_df[
    "Distance (km)"
]

model.warehouse_to_market_distance = pyo.Param(
    model.warehouse,
    model.market,
    initialize=warehouse_market_distance
)


# ---------- Global Parameters ----------

parameters = (
    parameters_df
    .set_index("Parameter")["Value"]
    .to_dict()
)

model.transportation_cost_per_ton_km = pyo.Param(
    initialize=parameters["Transportation Cost Per Ton-Km"]
)

model.tehran_qom_ratio = pyo.Param(
    initialize=parameters["Tehran Qom Ratio"]
)

model.ahvaz_receiving_limit = pyo.Param(
    initialize=parameters["Ahvaz Receiving Limit"]
)

model.mashhad_minimum_delivery = pyo.Param(
    initialize=parameters["Mashhad Minimum Delivery"]
)


# ---------- Initial Inventory ----------

initial_inventory = inventory_df.set_index(
    "Warehouse"
)["Initial Inventory"].to_dict()

model.initial_inventory = pyo.Param(
    model.warehouse,
    initialize=initial_inventory
)

# ==========================================================
# Decision Variables
# ==========================================================

# Monthly production quantity at each factory
model.production = pyo.Var(model.factory,model.time,domain=pyo.NonNegativeReals)

# Monthly shipment quantity from factories to warehouses
model.factory_to_warehouse_shipment = pyo.Var(
    model.factory,
    model.warehouse,
    model.time,
    domain=pyo.NonNegativeReals
)

# Monthly shipment quantity from warehouses to customer markets
model.warehouse_to_market_shipment = pyo.Var(
    model.warehouse,
    model.market,
    model.time,
    domain = pyo.NonNegativeReals
)

# Inventory level at each warehouse at the end of each month
model.inventory = pyo.Var(
    model.warehouse,
    model.time,
    domain=pyo.NonNegativeReals
)

# ==========================================================
# Constraints
# ==========================================================

# Factory Capacity Constraint
# Production at each factory cannot exceed its monthly capacity.
def factory_capacity_rule(model,factory,time):
    return(
        model.production[factory,time] 
        <= model.production_capacity[factory]
    )

model.factory_capacity_constraint = pyo.Constraint(
    model.factory,
    model.time,
    rule=factory_capacity_rule
)

# ----------------------------------------------------------
# Warehouse Capacity Constraint
# Inventory stored at each warehouse cannot exceed its capacity.
# ----------------------------------------------------------

def warehouse_capacity_rule(model, warehouse, time):
    return (
        model.inventory[warehouse, time]
        <= model.warehouse_capacity[warehouse]
    )


model.warehouse_capacity_constraint = pyo.Constraint(
    model.warehouse,
    model.time,
    rule=warehouse_capacity_rule
)

# ----------------------------------------------------------
# Inventory Balance Constraint
# Inventory conservation at each warehouse.
# ----------------------------------------------------------

def inventory_balance_rule(model, warehouse, time):

    incoming = sum(
        model.factory_to_warehouse_shipment[factory, warehouse, time]
        for factory in model.factory
    )

    outgoing = sum(
        model.warehouse_to_market_shipment[warehouse, market, time]
        for market in model.market
    )

    if time == "Jan":
        return (
            model.initial_inventory[warehouse]
            + incoming
            ==
            outgoing
            + model.inventory[warehouse, time]
        )

    previous_month = {
        "Feb": "Jan",
        "Mar": "Feb",
        "Apr": "Mar"
    }

    return (
        model.inventory[warehouse, previous_month[time]]
        + incoming
        ==
        outgoing
        + model.inventory[warehouse, time]
    )


model.inventory_balance_constraint = pyo.Constraint(
    model.warehouse,
    model.time,
    rule=inventory_balance_rule
)

# ----------------------------------------------------------
# Demand Satisfaction Constraint
# Customer demand must be fully satisfied in every period.
# ----------------------------------------------------------

def demand_satisfaction_rule(model,market,time):
    return(
        sum(
            model.warehouse_to_market_shipment[warehouse,market,time]
            for warehouse in model.warehouse
        )
        ==
        model.market_demand[market,time]
    
        )
model.demand_satisfaction_constraint = pyo.Constraint(
        model.market,
        model.time,
        rule=demand_satisfaction_rule
    )

# ----------------------------------------------------------
# Contractual Obligation Constraint
# At least 30% of Tehran factory production must be shipped
# through Qom distribution center.
# ----------------------------------------------------------

def contractual_obligation_rule(model, time):

    return (
        model.factory_to_warehouse_shipment["Tehran", "Qom", time]
        >=
        model.tehran_qom_ratio
        * model.production["Tehran", time]
    )


model.contractual_obligation_constraint = pyo.Constraint(
    model.time,
    rule=contractual_obligation_rule
)

# ----------------------------------------------------------
# Temporary Warehouse Restriction
# Due to maintenance, Ahvaz warehouse has a limited
# receiving capacity.
# ----------------------------------------------------------

def temporary_warehouse_rule(model, time):

    return (
        sum(
            model.factory_to_warehouse_shipment[factory, "Ahvaz", time]
            for factory in model.factory
        )
        <= model.ahvaz_receiving_limit
    )


model.temporary_warehouse_constraint = pyo.Constraint(
    model.time,
    rule=temporary_warehouse_rule
)

# ----------------------------------------------------------
# Customer Agreement Constraint
# At least 400 tons delivered to Mashhad market must be
# shipped from Mashhad distribution center.
# ----------------------------------------------------------

def customer_agreement_rule(model, time):

    return (
        model.warehouse_to_market_shipment["Mashhad", "Mashhad", time]
        >= model.mashhad_minimum_delivery
    )


model.customer_agreement_constraint = pyo.Constraint(
    model.time,
    rule=customer_agreement_rule
)

# ----------------------------------------------------------
# Factory Flow Balance Constraint
# All produced products must be shipped to warehouses.
# ----------------------------------------------------------

def factory_flow_balance_rule(model, factory, time):

    return (
        model.production[factory, time]
        ==
        sum(
            model.factory_to_warehouse_shipment[
                factory,
                warehouse,
                time
            ]
            for warehouse in model.warehouse
        )
    )


model.factory_flow_balance_constraint = pyo.Constraint(
    model.factory,
    model.time,
    rule=factory_flow_balance_rule
)
# ==========================================================
# Objective Function
# ==========================================================
# The objective is to minimize the total supply chain cost,
# including production, transportation, and inventory holding costs.
# ----------------------------------------------------------

model.objective = pyo.Objective(
    sense=pyo.minimize,
    expr=
        sum(
            model.production[factory, time]
            * model.production_cost[factory]
            for factory in model.factory
            for time in model.time
        )

        +

        sum(
            model.factory_to_warehouse_shipment[
                factory, warehouse, time
            ]
            * model.factory_to_warehouse_distance[
                factory, warehouse
            ]
            * model.transportation_cost_per_ton_km
            for factory in model.factory
            for warehouse in model.warehouse
            for time in model.time
        )

        +

        sum(
            model.warehouse_to_market_shipment[
                warehouse, market, time
            ]
            * model.warehouse_to_market_distance[
                warehouse, market
            ]
            * model.transportation_cost_per_ton_km
            for warehouse in model.warehouse
            for market in model.market
            for time in model.time
        )

        +

        sum(
            model.inventory[warehouse, time]
            * model.inventory_holding_cost[warehouse]
            for warehouse in model.warehouse
            for time in model.time
        )
)
# ==========================================================
# Solver
# ==========================================================

solver = pyo.SolverFactory("gurobi")

results = solver.solve(
    model,
    tee=True
)
# ==========================================================
# Results
# ==========================================================

print("\n" + "=" * 60)
print("Optimization Results")
print("=" * 60)

print("Solver Status:", results.solver.status)
print("Termination Condition:", results.solver.termination_condition)

total_cost = pyo.value(model.objective)

print("Total Supply Chain Cost:", total_cost)


# ==========================================================
# Export Results to Excel
# ==========================================================



output_file = os.path.join(
    project_root,
    "results",
    "Optimization_Results.xlsx"
)

# ----------------------------------------------------------
# 1. Summary
# ----------------------------------------------------------

summary_df = pd.DataFrame({
    "Metric": [
        "Solver Status",
        "Termination Condition",
        "Total Supply Chain Cost"
    ],
    "Value": [
        str(results.solver.status),
        str(results.solver.termination_condition),
        total_cost
    ]
})


# ----------------------------------------------------------
# 2. Production Results
# ----------------------------------------------------------

production_results = []

for factory in model.factory:
    for time in model.time:

        production_results.append({
            "Factory": factory,
            "Time": time,
            "Production (Ton)": pyo.value(
                model.production[factory, time]
            )
        })

production_df = pd.DataFrame(production_results)


# ----------------------------------------------------------
# 3. Factory to Warehouse Shipment Results
# ----------------------------------------------------------

factory_warehouse_results = []

for factory in model.factory:
    for warehouse in model.warehouse:
        for time in model.time:

            quantity = pyo.value(
                model.factory_to_warehouse_shipment[
                    factory,
                    warehouse,
                    time
                ]
            )

            factory_warehouse_results.append({
                "Factory": factory,
                "Warehouse": warehouse,
                "Time": time,
                "Shipment (Ton)": quantity
            })

factory_warehouse_df = pd.DataFrame(
    factory_warehouse_results
)


# ----------------------------------------------------------
# 4. Warehouse to Market Shipment Results
# ----------------------------------------------------------

warehouse_market_results = []

for warehouse in model.warehouse:
    for market in model.market:
        for time in model.time:

            quantity = pyo.value(
                model.warehouse_to_market_shipment[
                    warehouse,
                    market,
                    time
                ]
            )

            warehouse_market_results.append({
                "Warehouse": warehouse,
                "Market": market,
                "Time": time,
                "Shipment (Ton)": quantity
            })

warehouse_market_df = pd.DataFrame(
    warehouse_market_results
)


# ----------------------------------------------------------
# 5. Inventory Results
# ----------------------------------------------------------

inventory_results = []

for warehouse in model.warehouse:
    for time in model.time:

        inventory_results.append({
            "Warehouse": warehouse,
            "Time": time,
            "Ending Inventory (Ton)": pyo.value(
                model.inventory[warehouse, time]
            )
        })

inventory_df = pd.DataFrame(inventory_results)


# ----------------------------------------------------------
# 6. Demand Results
# ----------------------------------------------------------

demand_results = []

for market in model.market:
    for time in model.time:

        demand = pyo.value(
            model.market_demand[market, time]
        )

        supplied = sum(
            pyo.value(
                model.warehouse_to_market_shipment[
                    warehouse,
                    market,
                    time
                ]
            )
            for warehouse in model.warehouse
        )

        demand_results.append({
            "Market": market,
            "Time": time,
            "Demand (Ton)": demand,
            "Supplied (Ton)": supplied,
            "Difference (Ton)": supplied - demand
        })

demand_df = pd.DataFrame(demand_results)


# ==========================================================
# 7. Constraint Check
# ==========================================================

constraint_results = []


# ----------------------------------------------------------
# Factory Capacity
# ----------------------------------------------------------

for factory in model.factory:
    for time in model.time:

        production = pyo.value(
            model.production[factory, time]
        )

        capacity = pyo.value(
            model.production_capacity[factory]
        )

        constraint_results.append({
            "Constraint": "Factory Capacity",
            "Factory": factory,
            "Warehouse": "",
            "Market": "",
            "Time": time,
            "Actual": production,
            "Limit": capacity,
            "Slack": capacity - production
        })


# ----------------------------------------------------------
# Warehouse Capacity
# ----------------------------------------------------------

for warehouse in model.warehouse:
    for time in model.time:

        inventory = pyo.value(
            model.inventory[warehouse, time]
        )

        capacity = pyo.value(
            model.warehouse_capacity[warehouse]
        )

        constraint_results.append({
            "Constraint": "Warehouse Capacity",
            "Factory": "",
            "Warehouse": warehouse,
            "Market": "",
            "Time": time,
            "Actual": inventory,
            "Limit": capacity,
            "Slack": capacity - inventory
        })


# ----------------------------------------------------------
# Ahvaz Receiving Limit
# ----------------------------------------------------------

for time in model.time:

    received = sum(
        pyo.value(
            model.factory_to_warehouse_shipment[
                factory,
                "Ahvaz",
                time
            ]
        )
        for factory in model.factory
    )

    limit = pyo.value(
        model.ahvaz_receiving_limit
    )

    constraint_results.append({
        "Constraint": "Ahvaz Receiving Limit",
        "Factory": "",
        "Warehouse": "Ahvaz",
        "Market": "",
        "Time": time,
        "Actual": received,
        "Limit": limit,
        "Slack": limit - received
    })


# ----------------------------------------------------------
# Tehran-Qom Contract
# ----------------------------------------------------------

for time in model.time:

    qom_shipment = pyo.value(
        model.factory_to_warehouse_shipment[
            "Tehran",
            "Qom",
            time
        ]
    )

    tehran_production = pyo.value(
        model.production[
            "Tehran",
            time
        ]
    )

    required = (
        pyo.value(model.tehran_qom_ratio)
        * tehran_production
    )

    constraint_results.append({
        "Constraint": "Tehran-Qom Contract",
        "Factory": "Tehran",
        "Warehouse": "Qom",
        "Market": "",
        "Time": time,
        "Actual": qom_shipment,
        "Limit": required,
        "Slack": qom_shipment - required
    })


# ----------------------------------------------------------
# Mashhad Customer Agreement
# ----------------------------------------------------------

for time in model.time:

    shipment = pyo.value(
        model.warehouse_to_market_shipment[
            "Mashhad",
            "Mashhad",
            time
        ]
    )

    minimum = pyo.value(
        model.mashhad_minimum_delivery
    )

    constraint_results.append({
        "Constraint": "Mashhad Customer Agreement",
        "Factory": "",
        "Warehouse": "Mashhad",
        "Market": "Mashhad",
        "Time": time,
        "Actual": shipment,
        "Limit": minimum,
        "Slack": shipment - minimum
    })


constraint_df = pd.DataFrame(constraint_results)


# ==========================================================
# Export All Results
# ==========================================================

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    summary_df.to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

    production_df.to_excel(
        writer,
        sheet_name="Production",
        index=False
    )

    factory_warehouse_df.to_excel(
        writer,
        sheet_name="Factory_to_Warehouse",
        index=False
    )

    warehouse_market_df.to_excel(
        writer,
        sheet_name="Warehouse_to_Market",
        index=False
    )

    inventory_df.to_excel(
        writer,
        sheet_name="Inventory",
        index=False
    )

    demand_df.to_excel(
        writer,
        sheet_name="Demand",
        index=False
    )

    constraint_df.to_excel(
        writer,
        sheet_name="Constraint_Check",
        index=False
    )


print("\nResults successfully exported to:")
print(output_file)







