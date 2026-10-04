# CLAUDE.md

Undergraduate thesis (KLTN, FTU): robust multi-objective distribution network design for a personal care FMCG company in Java. Data comes from a real consulting project; the company has approved its use on condition of full anonymization.

## Working with the user

- The user writes in Vietnamese. Reply in Vietnamese. Thesis documents (`Decision_Log.md`, `Methodology & Result.md`, README) are written in English.
- Code comments in notebooks follow the existing style: Vietnamese, with `# ===== STEP =====` section headers.
- Timeline is tight: prioritize producing runnable output over polishing.

## Source of truth

- [Decision_Log.md](./Decision_Log.md) holds every scope, modeling and data decision with a status (✅ decided, 🔄 re-validate, ❓ open). Read it before proposing changes. Do not re-litigate ✅ items. When a decision is made or changed, update the log and its change log in the same turn.
- The method chain is fixed: **Bertsimas & Sim robust MOMILP → AUGMECON2 → TOPSIS**. Toolchain: Pyomo, HiGHS (`appsi_highs`), pyaugmecon, scikit-criteria (not pymcdm).
- `f2` is lead-time coverage (MCLP-style, threshold `L_max` days), not distance coverage and not average lead time.
- `Methodology & Result.md` only receives results that were actually produced by a notebook run. Never fill in numbers that were not computed.

## Anonymization (hard rule)

- Never write the company name, product names, brand names, customer names or site/facility names into thesis outputs: README, `Methodology & Result.md`, figures, exported tables, printed notebook output intended for the thesis. Refer to "the Company" and use anonymized IDs.
- `Document/` and `Raw Data/` contain the company's internal material. Reference only; never quote them into shareable outputs, never publish them (Artifacts, gists, external services).
- The GitHub remote (`origin`) must not receive company-named files or data. Check before any commit or push.

## Layout

- `Raw Data/`: source parquet files, read-only. Never modify or overwrite. Scenario subfolders `0,1_Baseline2025/` and `3_GF_Unconstrained/`.
- `Notebook/Validation.ipynb`: cleaning and validation, run first. Writes to `Model - Data used/`.
- `Notebook/Model.ipynb`: parameters, Pyomo model, AUGMECON2, TOPSIS. Reads only from `Model - Data used/`.
- `Model Outputs/`: Pareto set, rankings, figures.
- `Document/`: company working documents (methodology notes for cost, CO2, lead time, ship-to grouping, network map, data dictionary).
- Use paths relative to the repo root (`D:\KLTN\Data`), not the old `Data Dictionary\...` paths.

## Data handling

- `B2B_SO_2025_JantoNov.parquet` is ~2 GB / 25M rows. Always load with `columns=[...]`; never load all 27 columns.
- Sales orders contain cancelled picking rows re-issued under the same `SOLineID`; including them double-counts demand (see Decision_Log 5.1).
- Every cleaning step prints before/after row counts and ends with `assert` checks (unique keys, no orphans, no nulls in model inputs). Report how much volume (kg) each filter removes.
- Volume unit is pallets (`kg / KGPerPallet`); time unit is monthly.
- Parquet and CSV are git-ignored; keep it that way.

## Environment

- Windows; Python with pandas 3.x, pyarrow. Set `PYTHONIOENCODING=utf8` when printing Vietnamese text from scripts in the shell.
- Run notebooks top to bottom (Restart & Run All) before trusting any output; stale cell outputs have caused confusion before.
