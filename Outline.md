# Outline — Model.ipynb

## 1. Environment & Library Setup
- 1.1. Import Libraries (Pyomo, HiGHS, Skcriteria, Pandas...)
- 1.2. Global Configurations & Random Seed

## 2. Data Ingestion & Preprocessing
- 2.1. Load Raw Datasets (Demand, Facility, Distance Matrix)
- 2.2. Data Cleaning & Spatial Aggregation (Clustering)
- 2.3. Uncertainty Parameter Extraction (d_bar, d_hat, Gamma)

## 3. Data Validation & Model Parameters
- 3.1. Schema & Data Integrity Checks (Pydantic / Assertions)
- 3.2. Index Sets & Parameter Dictionaries for Pyomo

## 4. Mathematical Model Formulation (Pyomo)
- 4.1. Decision Variables (Binary Y, Continuous Flow Z, Robust Duals z, p)
- 4.2. Objective Functions (f1: Cost, f2: Lead Time, f3: CO2)
- 4.3. Constraints (Robust Demand, DC Capacities, Flow Conservation)

## 5. Multi-Objective Optimization (AUGMECON2 Execution)
- 5.1. Payoff Table Construction (Individual Min/Max)
- 5.2. Epsilon-Grid Sweeping & Solver Execution (HiGHS)
- 5.3. Extraction of Non-Dominated Pareto Set

## 6. Multi-Criteria Decision Making (TOPSIS Ranking)
- 6.1. Decision Matrix Construction & Vector Normalization
- 6.2. Scenario Weighting (Cost-Driven, Service-Driven, Balanced)
- 6.3. Best Compromise Solution Selection

## 7. Output Export & Visual Analytics
- 7.1. 2D / 3D Pareto Frontier Visualization
- 7.2. Optimal Network Configuration Map (Active DCs & Flows)
- 7.3. Export Results (Excel / Parquet / CSV)
