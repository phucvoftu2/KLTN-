# Methodology & Result

Rewritten from scratch on 2026-10-04. Sections are filled in as each stage is built and validated. Nothing below is a result until its section says so.

Decisions behind this document: see [Decision_Log.md](./Decision_Log.md).

---

## 1. Problem statement

*To write.* Which facilities to open and how to route product from the factory through the network to B2B demand nodes in Java, trading off cost, service and CO2.

## 2. Data and cleaning

*To write after the cleaning rerun.* For each source table: origin, rows before and after each rule, rule rationale, validation checks passed.

| Table | Rows raw | Rows clean | Rules applied | Checks |
|---|---|---|---|---|
| Sales orders | | | | |
| Customer master | | | | |
| Product master | | | | |
| Ship-to group mapping | | | | |
| Facility master | | | | |
| Cost tables (supply, transfer, last-mile) | | | | |
| Lead-time table | | | | |

## 3. Mathematical model

### 3.1 Sets, parameters, variables
*To write.*

### 3.2 Objectives
- `f1` Total Cost
- `f2` Uncovered demand by lead-time coverage (`L_max`)
- `f3` CO2

### 3.3 Constraints
*To write.* Flow balance, demand satisfaction, throughput capacity, facility linking, fixed backbone, coverage.

## 4. Solution method

### 4.1 AUGMECON2
*To write.* Payoff table, ε-grid, augmentation term, bypass.

### 4.2 TOPSIS
*To write.* Decision matrix, normalization, weight scenarios.

## 5. Results

*Pending.*

### 5.1 Single-objective `f1` and demand sensitivity
### 5.2 Pareto frontier
### 5.3 TOPSIS ranking by weight scenario
### 5.4 Selected network configuration

## 6. Discussion and limitations

*Pending.*
