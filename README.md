# Multi-Period Multi-Echelon Supply Chain Network Optimization

An optimization model for a multi-period, multi-echelon dairy supply chain network, developed using Python, Pyomo, and Gurobi.

The model determines optimal production, transportation, and inventory decisions across a four-month planning horizon while minimizing the total supply chain operating cost.
## Overview

This project develops a mathematical optimization model for a hypothetical nationwide dairy supply chain operated by Pars Dairy Co.

The supply chain consists of manufacturing plants, regional distribution centers, and customer markets. Products are manufactured at factories, transported to distribution centers, and then delivered to customer markets.

The model considers a four-month planning horizon covering January through April. Production, transportation, and inventory decisions are optimized simultaneously to satisfy all customer demand at minimum total supply chain cost.
## Supply Chain Structure

The modeled supply chain consists of three main echelons:

- Manufacturing Plants
- Distribution Centers
- Customer Markets

Products flow through the network according to the following structure:

Manufacturing Plants
        │
        ▼
Distribution Centers
        │
        ▼
Customer Markets
 
## Optimization Model


The supply chain network is formulated as a linear programming optimization model.

The model simultaneously determines production, transportation, and inventory decisions over a four-month planning horizon while satisfying operational and contractual constraints.

### Planning Horizon

The planning horizon consists of four monthly periods:

- January
- February
- March
- April

Transportation lead time is assumed to be zero, meaning that shipments made during a given month are available within the same planning period.

### Decision Variables

The model includes four main decision variables:

| Decision Variable | Description |
|---|---|
| `Production[f,t]` | Quantity produced by factory `f` during period `t` |
| `Shipment_FW[f,w,t]` | Quantity shipped from factory `f` to warehouse `w` during period `t` |
| `Shipment_WM[w,m,t]` | Quantity shipped from warehouse `w` to market `m` during period `t` |
| `Inventory[w,t]` | Ending inventory at warehouse `w` during period `t` |

All decision variables are continuous and non-negative.

### Objective Function

The objective is to minimize the total supply chain cost:

$$
\begin{aligned}
TotalSupplyChainCost =\;& ProductionCost \\
&+ FactoryToWarehouseTransportationCost \\
&+ WarehouseToMarketTransportationCost \\
&+ InventoryHoldingCost
\end{aligned}
$$


---


## Key Constraints

The optimization model incorporates the following operational and business constraints:

### 1. Factory Capacity

Monthly production at each factory cannot exceed its available production capacity.

$$
Production_{f,t} \leq ProductionCapacity_f
$$

for every factory $f$ and planning period $t$.
### 2. Warehouse Capacity

Ending inventory at each distribution center cannot exceed its storage capacity.

$$
Inventory_{w,t} \leq WarehouseCapacity_w
$$

for every distribution center $w$ and planning period $t$.

### 3. Inventory Balance

Inventory is balanced across consecutive periods according to:

$$
BeginningInventory_{w,t}
+
\sum_{f \in F} Shipment^{FW}_{f,w,t}
-
\sum_{m \in M} Shipment^{WM}_{w,m,t}
=
Inventory_{w,t}
$$

For the first planning period, the initial inventory of each distribution center is used as the beginning inventory:

$$
InitialInventory_w
+
\sum_{f \in F} Shipment^{FW}_{f,w,January}
-
\sum_{m \in M} Shipment^{WM}_{w,m,January}
=
Inventory_{w,January}
$$

For subsequent periods:

$$
Inventory_{w,t-1}
+
\sum_{f \in F} Shipment^{FW}_{f,w,t}
-
\sum_{m \in M} Shipment^{WM}_{w,m,t}
=
Inventory_{w,t}
$$

### 4. Demand Satisfaction

The demand of every customer market must be fully satisfied in every planning period.

$$
\sum_{w \in W} Shipment^{WM}_{w,m,t}
=
Demand_{m,t}
$$

for every market $m$ and planning period $t$.

Shortages are not permitted.

### 5. Tehran–Qom Contractual Obligation

At least 30% of the production from the Tehran Factory must be shipped through the Qom Distribution Center in each planning period.

$$
Shipment^{FW}_{Tehran,Qom,t}
\geq
0.30 \times Production_{Tehran,t}
$$

for every planning period $t$.

### 6. Ahvaz Receiving Restriction

Due to temporary maintenance activities, the Ahvaz Distribution Center can receive at most 1,200 tons per month.

$$
\sum_{f \in F} Shipment^{FW}_{f,Ahvaz,t}
\leq
1200
$$

for every planning period $t$.

### 7. Mashhad Customer Agreement

At least 400 tons per month delivered to the Mashhad Market must originate from the Mashhad Distribution Center.

$$
Shipment^{WM}_{Mashhad,Mashhad,t}
\geq
400
$$

for every planning period $t$.

### 8. Factory Flow Balance

All products manufactured at each factory during a planning period must be shipped to distribution centers during the same period.

$$
Production_{f,t}
=
\sum_{w \in W} Shipment^{FW}_{f,w,t}
$$

for every factory $f$ and planning period $t$.

## Input Data

The optimization model uses an Excel workbook as its primary data source. The input data are organized into separate worksheets to maintain a clear and structured data-management process.

### Factory Data

The `Factory` worksheet contains information related to manufacturing plants:

- Factory name
- Monthly production capacity
- Production cost per ton

### Warehouse Data

The `Warehouse` worksheet contains information related to distribution centers:

- Warehouse name
- Storage capacity
- Inventory holding cost per ton per month

### Market Data

The `Market` worksheet contains monthly customer demand for each market:

- Market name
- January demand
- February demand
- March demand
- April demand

### Factory-to-Warehouse Distance

The `Factory_Warehouse_Distance` worksheet contains the transportation distances between manufacturing plants and distribution centers.

### Warehouse-to-Market Distance

The `Warehouse_Market_Distance` worksheet contains the transportation distances between distribution centers and customer markets.

### Initial Inventory

The `Initial_Inventory` worksheet contains the inventory available at each distribution center at the beginning of the planning horizon.

### Model Parameters

The `Parameters` worksheet contains the global parameters used by the optimization model, including:

- Transportation cost per ton-kilometer
- Tehran–Qom contractual ratio
- Ahvaz receiving limit
- Minimum monthly delivery from Mashhad Distribution Center to Mashhad Market

## Mathematical Formulation
### Sets

The following index sets are used to formulate the supply chain optimization model:

| Set | Description |
|---|---|
| $F$ | Set of manufacturing plants |
| $W$ | Set of distribution centers |
| $M$ | Set of customer markets |
| $T$ | Set of planning periods |

The planning horizon consists of four monthly periods:
$$
T = \{Jan, Feb, Mar, Apr\}
$$
### Parameters

The following parameters are used to define the operational characteristics, costs, transportation distances, customer demand, and business requirements of the supply chain network.

#### Factory Parameters

| Parameter | Description | Unit |
|---|---|---|
| $ProductionCapacity_f$ | Maximum monthly production capacity of factory $f$ | Ton/month |
| $ProductionCost_f$ | Production cost at factory $f$ | Toman/ton |

#### Warehouse Parameters

| Parameter | Description | Unit |
|---|---|---|
| $WarehouseCapacity_w$ | Maximum storage capacity of warehouse $w$ | Ton |
| $HoldingCost_w$ | Inventory holding cost at warehouse $w$ | Toman/ton/month |
| $InitialInventory_w$ | Initial inventory available at warehouse $w$ at the beginning of the planning horizon | Ton |

#### Market Parameters

| Parameter | Description | Unit |
|---|---|---|
| $Demand_{m,t}$ | Customer demand at market $m$ during period $t$ | Ton |

#### Transportation Parameters

| Parameter | Description | Unit |
|---|---|---|
| $Distance^{FW}_{f,w}$ | Transportation distance from factory $f$ to warehouse $w$ | km |
| $Distance^{WM}_{w,m}$ | Transportation distance from warehouse $w$ to market $m$ | km |
| $TransportationCost$ | Transportation cost per ton-kilometer | Toman/ton-km |

#### Business Parameters

| Parameter | Description | Unit |
|---|---|---|
| $TehranQomRatio$ | Minimum proportion of Tehran Factory production that must be shipped through Qom Distribution Center | Ratio |
| $AhvazReceivingLimit$ | Maximum quantity that can be received by Ahvaz Distribution Center per month | Ton/month |
| $MashhadMinimumDelivery$ | Minimum monthly quantity delivered from Mashhad Distribution Center to Mashhad Market | Ton/month |

### Decision Variables

The optimization model determines four main categories of decision variables:

| Variable | Description | Unit |
|---|---|---|
| $Production_{f,t}$ | Quantity produced by factory $f$ during period $t$ | Ton |
| $Shipment^{FW}_{f,w,t}$ | Quantity shipped from factory $f$ to warehouse $w$ during period $t$ | Ton |
| $Shipment^{WM}_{w,m,t}$ | Quantity shipped from warehouse $w$ to market $m$ during period $t$ | Ton |
| $Inventory_{w,t}$ | Ending inventory at warehouse $w$ during period $t$ | Ton |

All decision variables are continuous and non-negative:

$$
Production_{f,t} \geq 0
$$

$$
Shipment^{FW}_{f,w,t} \geq 0
$$

$$
Shipment^{WM}_{w,m,t} \geq 0
$$

$$
Inventory_{w,t} \geq 0
$$
for all applicable combinations of factories, warehouses, markets, and planning periods.
### Objective Function

The objective of the model is to minimize the total supply chain operating cost.

The total cost consists of four main components:

1. Production cost
2. Factory-to-warehouse transportation cost
3. Warehouse-to-market transportation cost
4. Inventory holding cost

The objective function is formulated as:

\[
\min Z =
\sum_{f \in F}\sum_{t \in T}
Production_{f,t} \times ProductionCost_f
 
+
\sum_{f \in F}\sum_{w \in W}\sum_{t \in T}
Shipment^{FW}_{f,w,t}
\times Distance^{FW}_{f,w}
\times TransportationCost
\]

\[
+
\sum_{w \in W}\sum_{m \in M}\sum_{t \in T}
Shipment^{WM}_{w,m,t}
\times Distance^{WM}_{w,m}
\times TransportationCost
\]

\[
+
\sum_{w \in W}\sum_{t \in T}
Inventory_{w,t}
\times HoldingCost_w
\]

where $Z$ represents the total supply chain operating cost.

### Constraints

The optimization model is subject to the following operational and business constraints.

#### 1. Factory Capacity Constraint

The production quantity at each factory cannot exceed its available production capacity in any planning period.

\[
Production_{f,t}
\leq
ProductionCapacity_f
\qquad
\forall f \in F,\; t \in T
\]

#### 2. Warehouse Capacity Constraint

The ending inventory at each distribution center cannot exceed its storage capacity.

\[
Inventory_{w,t}
\leq
WarehouseCapacity_w
\qquad
\forall w \in W,\; t \in T
\]

#### 3. Inventory Balance Constraint

Inventory conservation must be maintained at every distribution center during each planning period.

For the first planning period:

$$
InitialInventory_w
+
\sum_{f \in F} Shipment^{FW}_{f,w,t}
=
\sum_{m \in M} Shipment^{WM}_{w,m,t}
+
Inventory_{w,t}
$$

For subsequent periods:

$$
Inventory_{w,t-1}
+
\sum_{f \in F} Shipment^{FW}_{f,w,t}
=
\sum_{m \in M} Shipment^{WM}_{w,m,t}
+
Inventory_{w,t}
$$

$$
\forall w \in W,\quad t \in T
$$

#### 4. Demand Satisfaction Constraint

The total quantity delivered to each customer market must exactly satisfy its demand in every planning period.

\[
\sum_{w \in W} Shipment^{WM}_{w,m,t}
=
Demand_{m,t}
\qquad
\forall m \in M,\; t \in T
\]

#### 5. Tehran–Qom Contractual Obligation

At least 30% of the production from Tehran Factory must be shipped through Qom Distribution Center in every planning period.

\[
Shipment^{FW}_{Tehran,Qom,t}
\geq
TehranQomRatio
\times
Production_{Tehran,t}
\qquad
\forall t \in T
\]

where:

\[
TehranQomRatio = 0.30
\]

#### 6. Ahvaz Receiving Restriction

The total quantity received by Ahvaz Distribution Center cannot exceed 1,200 tons in any planning period.

\[
\sum_{f \in F}
Shipment^{FW}_{f,Ahvaz,t}
\leq
AhvazReceivingLimit
\qquad
\forall t \in T
\]

where:

\[
AhvazReceivingLimit = 1200
\]

#### 7. Mashhad Customer Agreement

At least 400 tons must be delivered from Mashhad Distribution Center to Mashhad Market in every planning period.

\[
Shipment^{WM}_{Mashhad,Mashhad,t}
\geq
MashhadMinimumDelivery
\qquad
\forall t \in T
\]

where:

\[
MashhadMinimumDelivery = 400
\]

#### 8. Factory Flow Balance Constraint

All products manufactured at each factory during a planning period must be shipped to distribution centers during the same period.

\[
Production_{f,t}
=
\sum_{w \in W}
Shipment^{FW}_{f,w,t}
\qquad
\forall f \in F,\; t \in T
\]

## Results

The optimization model was solved using the Gurobi optimization solver.

The model was successfully solved to optimality, producing an optimal supply chain plan for the four-month planning horizon.

### Solver Performance

| Metric | Result |
|---|---:|
| Solver | Gurobi |
| Solver Status | Optimal |
| Termination Condition | Optimal |
| Total Supply Chain Cost | 901,705,250,000 Toman |

The optimal solution determines the production, transportation, and inventory decisions required to satisfy all customer demand while respecting the operational and contractual constraints of the supply chain network.


