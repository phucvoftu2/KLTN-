# KLTN: Trade-off Analysis in Personal Care Supply Chain Distribution Network

**An Application of an Integrated MOO-MCDM Framework**

Undergraduate thesis, Foreign Trade University (FTU), Logistics & Supply Chain Management. The case is a personal care FMCG company's distribution network in Java, Indonesia. The company is anonymized in all thesis outputs.

## Problem

Decide which last-mile and regional facilities to open, and how to route product from one factory source through the network to B2B demand nodes, so that three objectives are balanced:

- `f1` total cost (minimize)
- `f2` uncovered demand, where a node is covered if an open facility reaches it within a lead-time limit (minimize)
- `f3` CO2 emissions, GLEC framework (minimize)

## Method

1. **Deterministic MOMILP** in Pyomo (demand = mean monthly pallets; demand sensitivity +10%, +20%).
2. **AUGMECON2** (Mavrotas & Florios, 2013) for the exact Pareto frontier, solved with HiGHS.
3. **TOPSIS** to rank Pareto solutions under Cost-driven, Service-driven and Balanced weights.

## Scope

Java only (truck), B2B only, one aggregated product in pallets, observed Jan–Nov 2025 data. See [Decision_Log.md](./Decision_Log.md) for every decision and its status.

## Repository structure

```
├── Raw Data/                  # Source parquet files (not tracked by git)
├── Notebook/
│   ├── Validation.ipynb       # Cleaning and validation, run first
│   └── Model.ipynb            # Parameters, Pyomo model, AUGMECON2, TOPSIS
├── Document/                  # Company working documents (reference only, not for sharing)
│   ├── Assumption documents/
│   ├── CO2/
│   ├── Lead time/
│   ├── Model - Notion/
│   ├── Product Master Cleaning/
│   ├── Ship-To Grouping/
│   ├── Transportation cost/
│   ├── Network Map.md
│   └── Data_Dictionary.xlsx
├── Model - Data used/         # Cleaned data written by Validation.ipynb (not tracked)
├── Model Outputs/             # Pareto set, TOPSIS ranking, figures
├── Decision_Log.md            # Scope, modeling and data decisions
├── Methodology & Result.md    # Formal method and results, written as stages complete
├── Outline.md                 # Model.ipynb outline
├── Backlog.md                 # Scope contingencies to revisit
├── CLAUDE.md                  # Working rules for Claude Code in this repo
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

Run `Notebook/Validation.ipynb` first, then `Notebook/Model.ipynb`.

## Status (2026-10-04)

Topic and data use approved by the company. Data pipeline is being rerun from raw files. Single-objective `f1` model with Γ sensitivity ran on the previous cleaning; it will be rerun on the new clean data. `f2`, `f3`, AUGMECON2 and TOPSIS are not built yet.

## Author

Phuc, Logistics & Supply Chain Management, FTU.
