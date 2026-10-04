# Decision Log

Single source of truth for scope, modeling and data decisions. Rewritten from scratch on 2026-10-04 when the data pipeline was restarted after the topic was approved. Earlier versions are in git history.

**Status legend:** ✅ Decided · 🔄 Carried over from the previous iteration, must be re-validated during the data rerun · ❓ Open

**Naming rule:** the company is anonymized in every thesis output ("the Company"). No company, product, customer or site names in the thesis text, notebooks' printed output, figures or README. Source documents in `Document/` are internal working material and are not for sharing.

---

## 1. Thesis identity

| # | Decision | Status |
|---|---|---|
| 1.1 | Working title: *Trade-off Analysis in Personal Care Supply Chain Distribution Network: An Application of an Integrated MOO-MCDM Framework* | ✅ |
| 1.2 | Topic and use of the company case and data approved by the company (2026-10-04), on condition of full anonymization | ✅ |
| 1.3 | Method chain is fixed: **Bertsimas & Sim robust MOMILP → AUGMECON2 → TOPSIS** | ✅ |
| 1.4 | Free optimization: the solver decides facility open/close (binary `Y_j`). No forced routing shares | ✅ |
| 1.5 | Toolchain: Python, Pyomo, HiGHS, pyaugmecon, scikit-criteria | ✅ |
| 1.6 | Build order: validate `f1` alone as a single-objective MILP first, then add `f2`, `f3`, then AUGMECON2 and TOPSIS. A sequencing choice, not a scope change | ✅ |

## 2. Scope

| # | Decision | Status |
|---|---|---|
| 2.1 | Geography: **Java only**, single-mode (truck). No sea or ferry legs | ✅ |
| 2.2 | Channel: **B2B only** | ✅ |
| 2.3 | Product: **one aggregated product**, volume in pallets (`kg / KGPerPallet`) | ✅ |
| 2.4 | Time basis: observed Jan–Nov 2025, monthly units, no forecast year and no extrapolation | 🔄 |
| 2.5 | Network is a segment of the Company's full network, kept small enough to stay controllable. Final cut to be agreed with the company contact | ❓ |
| 2.6 | Definition of "trade-offs" (which objectives are traded and why finance must arbitrate) to be agreed with the company contact | ❓ |

## 3. Objectives

| # | Decision | Status |
|---|---|---|
| 3.1 | `f1` Total Cost (min): fixed facility cost `Y_j`, supply, transfer, last-mile delivery. Handling and storage-penalty terms to be confirmed against data | 🔄 |
| 3.2 | `f2` Service, **lead-time coverage (MCLP-style)**: minimize uncovered demand `Σ d_k·U_k`, where node `k` is covered if at least one open facility reaches it within `L_max` days. Uses the route-level `TotalLeadTimeInDays` table | ✅ |
| 3.3 | `f3` CO2 (min): GLEC emission factors × tonne-km (transport) + per-tonne warehousing factor | 🔄 |
| 3.4 | `L_max` (days) | ❓ |
| 3.5 | Distance for `f3` comes from the route distance table (road distance), not Haversine | 🔄 |

## 4. Network structure

| # | Decision | Status |
|---|---|---|
| 4.1 | Supply origin: factories merged into one node, co-located with the NDC, supply cost 0, supply unconstrained (no manufacturing optimization) | ✅ |
| 4.2 | Java facilities in scope: NDC fixed open; DEPO, RDC, DC Direct, DC Satellite are decision candidates; FC and Instant Hub excluded (B2C-oriented). Gives 22 facilities (1 fixed, 21 decision) | 🔄 |
| 4.3 | Transfer arcs restricted to the hierarchical flow types observed in the transfer cost table | 🔄 |
| 4.4 | Capacity as monthly throughput: `CapacityInPallet × 30 / DOS`. Using raw static capacity as throughput made the model infeasible | 🔄 |
| 4.5 | DOS aggregated by median per facility; DEPO facilities (cross-dock) set to 0 and given a large-M throughput | 🔄 |
| 4.6 | Demand nodes `K` = the Company's existing ship-to groups (clean many-to-one mapping from ship-to) | 🔄 |

## 5. Data cleaning rules (rerun from raw data)

| # | Decision | Status |
|---|---|---|
| 5.1 | Sales orders: keep **`OrderStatus = Done` only**. The raw file contains cancelled picking rows that were re-issued under the same `SOLineID` and delivered, so counting cancelled rows double-counts demand (3.18M cancelled rows; ~102k lines appear both cancelled and done) | ❓ confirm |
| 5.2 | Demand quantity: `QtyDeliveredInKG` of Done rows (actual shipped volume) rather than `QtyOrderedInKG` | ❓ confirm |
| 5.3 | Drop rows with non-positive quantity and exact duplicate rows | 🔄 |
| 5.4 | Product scope: segments Beauty and Personal Care only; drop products with `KGPerPallet` < 10 or > 2000 (data errors). Report the share of volume removed | 🔄 |
| 5.5 | Customer master: fix the single Java ship-to with out-of-country coordinates; drop rows with missing coordinates | 🔄 |
| 5.6 | Keep only Java B2B ship-tos present in the ship-to group mapping | 🔄 |
| 5.7 | Cost tables: use the Unconstrained / Greenfield scenario for transfer and last-mile (free-flow cost, not forced to historical routes); filter both origin and destination to the 22 in-scope facilities and the in-scope demand nodes | 🔄 |
| 5.8 | Each cleaning step prints before/after counts and ends with assertions (keys unique, no orphans, no nulls in model inputs) | ✅ |
| 5.9 | Demand parameters per node: `d̄_k` = mean monthly pallets, `d̂_k` = max monthly minus mean, zero-filled months included | 🔄 |

## 6. Uncertainty and solution method

| # | Decision | Status |
|---|---|---|
| 6.1 | Robust demand via Bertsimas & Sim budget of uncertainty `Γ`, no probability assumptions | ✅ |
| 6.2 | `Γ` sensitivity scan; current test range 0 to 1 | 🔄 |
| 6.3 | AUGMECON2 over `f1, f2, f3`: payoff table, ε-grid on two objectives, HiGHS | ✅ |
| 6.4 | TOPSIS with three weight scenarios: Cost-driven, Service-driven, Balanced | ✅ |

## 7. Open items

- [ ] Lead-time table (`LeadTime_AllFlow.parquet`) is not in `Raw Data/` yet. Copy it in, then check coverage of facility to demand-node pairs for Java.
- [ ] Choose `L_max` (candidate: company service levels, Java within 1 day, outer Java within 3 days).
- [ ] Confirm 5.1 and 5.2 (cancelled rows, ordered vs delivered quantity).
- [ ] Agree the network segment (2.5) and the trade-off definition (2.6) with the company contact.
- [ ] Build the anonymization map (facility, customer group and product labels) and apply it to every output before sharing.
- [ ] Decide `Γ` range and AUGMECON2 grid size.
- [ ] Decide whether cost rates stay on a 2025 basis (default) or get a flat inflation index.
- [ ] Remove the company-named files from the public GitHub repository, or make the repository private.

## 8. Change log

| Date | Change |
|---|---|
| 2026-10-04 | Log rewritten. Topic approved. `f2` switched to lead-time coverage. Data pipeline to be rerun from raw files. Repository folders reorganized (`Document/`, `Raw Data/`, `Notebook/`) |
