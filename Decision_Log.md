# Decision Log

Single source of truth for scope, modeling and data decisions. Rewritten from scratch on 2026-10-04 when the data pipeline was restarted after the topic was approved. Earlier versions are in git history.

**Status legend:** ✅ Decided · 🔄 Carried over from the previous iteration, must be re-validated during the data rerun · ❓ Open

**Naming rule:** the company is anonymized in every thesis output ("the Company"). No company, product, customer or site names in the thesis text, notebooks' printed output, figures or README. Source documents in `Document/` are internal working material and are not for sharing.

---

## 1. Thesis identity

| # | Decision | Status |
|---|---|---|
| 1.1 | Working title: *Trade-off Analysis in Personal Care Supply Chain Distribution Network: An Indonesian Case Study* (changed 2026-10-06; previous subtitle: "An Application of an Integrated MOO-MCDM Framework") | ✅ |
| 1.2 | Topic and use of the company case and data approved by the company (2026-10-04), on condition of full anonymization | ✅ |
| 1.3 | Method chain is fixed: **Bertsimas & Sim robust MOMILP → AUGMECON2 → TOPSIS** | ✅ |
| 1.4 | Free optimization: the solver decides facility open/close (binary `Y_j`). No forced routing shares | ✅ |
| 1.5 | Toolchain: Python, Pyomo, HiGHS, pyaugmecon, scikit-criteria | ✅ |
| 1.6 | Build order: validate `f1` alone as a single-objective MILP first, then add `f2`, `f3`, then AUGMECON2 and TOPSIS. A sequencing choice, not a scope change | ✅ |

## 2. Scope

| # | Decision | Status |
|---|---|---|
| 2.1 | Geography: **all of Indonesia** (every Indonesian island), no Indonesian customers excluded. **Malaysia excluded** (2026-10-04): the study is conducted on the Indonesian network. Replaces the earlier Java-only limit. Sea / ferry legs are in scope, taken from the lead-time table | ✅ |
| 2.2 | Channel: **B2B only; B2C excluded** (2026-10-04). Reasons: B2C `ShipToID`s are e-commerce platform hubs, not consumers, so B2C demand cannot be placed on a city; the company itself built B2C demand from a separate file we do not have and modeled B2C last-mile cost as 0; B2C runs through its own facility types (FC / Instant Hub). Stated as a delimitation: B2C = 15.8% of delivered kg | ✅ |
| 2.3 | Product: **one aggregated product**, volume in pallets (`kg / KGPerPallet`) | ✅ |
| 2.4 | Time basis: observed Jan–Nov 2025, monthly units, no forecast year and no extrapolation. Future demand risk is handled by the robust budget `Γ`; an optional demand-growth sensitivity (+10–20% on `d̄`) may be added in results | ✅ |
| 2.6 | Definition of "trade-offs" (which objectives are traded and why finance must arbitrate) to be agreed with the company contact | ❓ |

## 3. Objectives

| # | Decision | Status |
|---|---|---|
| 3.1 | `f1` Total Cost (min): fixed facility cost `Y_j`, supply, transfer, last-mile delivery, plus B2B handling cost per pallet of outbound volume. **Handling comes from the Baseline facility master (2025 basis)**: GF handling is ≈1.41× Baseline (range 1.39–1.43, i.e. inflated to 2030 with non-uniform factors), so Baseline is used directly instead of deflating. **No storage-penalty term**: in the company's model it replaces capacity in the optimized scenario (GF penalty ≈ 0.136× Baseline, a different unit/concept); our MILP uses fixed cost × `Y_j` plus a hard capacity instead | ✅ |
| 3.2 | `f2` Service, **lead-time coverage (MCLP-style)**: minimize uncovered demand `Σ d_k·U_k`, where node `k` is covered if at least one open facility reaches it within `L_max` days. Uses the route-level `TotalLeadTimeInDays` table | ✅ |
| 3.3 | `f3` CO2 (min): GLEC emission factors × tonne-km (transport) + per-tonne warehousing factor | 🔄 |
| 3.4 | `L_max` (days) | ❓ |
| 3.5 | Distance for `f3` comes from the route distance table (road distance), not Haversine | 🔄 |

## 4. Network structure

| # | Decision | Status |
|---|---|---|
| 4.1 | Supply origin: factories merged into one node, co-located with the NDC, supply cost 0, supply unconstrained (no manufacturing optimization) | ✅ |
| 4.1a | No Batang factory (future site in the company's 2030 scenario). Supply = current factories → current NDC only; Batang factory/NDC lanes in the GF tables are excluded (2026-10-04) | ✅ |
| 4.2 | Candidate facility set = **existing facilities only** (Baseline facility master, 67). NDC fixed open; all others are `Y_j` decisions. **FC (11) and Instant Hub (2) are excluded**: profile 2.3c shows they have 0 B2B last-mile lanes and shipped 0 t B2B in 2025. Result: **53 facilities = 1 NDC (fixed open) + 52 `Y_j` decisions** (RDC 9, DC Direct 7, DC Satellite 18, DEPO 18), after dropping the Malaysian DC (2.1). Note: sales-order `FacilityID` is the physical code (e.g. `D36`) while the model uses `LocationID` (e.g. `MWH_D36`), so historical shipments must be joined via that prefix, not directly (2026-10-04) | ✅ |
| 4.2a | **The 71 greenfield candidate sites of the GF facility master are excluded**, as is NDC Batang. They have `FacilityType = Unknown`, capacity 0 and no own cost, so including them would rest entirely on our own assumptions. (They come from the company's K-medoids demand clustering, Assumption doc §4.2.) Stated as a delimitation: the thesis re-optimizes the existing network, it does not site new facilities (2026-10-04) | ✅ |
| 4.2b | ~~Malaysian DC code mismatch (`MWH_M02` → `MWH_M04`)~~: moot since Malaysia is excluded (2.1) | ✅ |
| 4.3 | Transfer arcs = all 369 GF transfer lanes between the 53 facilities (company candidate set, deflated ÷ 1.1546). Includes lateral and some "upward" flows (e.g. DC Satellite → RDC 38, DC Satellite → DC Satellite 67), not only the strict top-down hierarchy assumed earlier. Every facility is reachable from the NDC. Kept as-is (restricting to a hierarchy would be our own assumption); 2 lanes differ from BL × 1.1546 by ≤ 5% (NDC → MWH_D14, NDC → MWH_D19), accepted. **Main run uses the company's lane sets as-is** (transfer 369, last-mile 14,770): they are model inputs already filtered by the company's rules (SLA 150 / 500 km, inter-island combinations, DC → DEPO ≤ 200 km, possibly the run-2 heuristics), not complete matrices. Candidate lane sets are standard practice; stated as a delimitation. Whether the lane set restricts the solution is tested after `f1` is solved (Backlog §2), not before (2026-10-06) | ✅ |
| 4.4 | Capacity as monthly throughput: `CapacityInPallet × 30 / DOS`. Using raw static capacity as throughput made the model infeasible | 🔄 |
| 4.4a | Capacity and fixed storage cost come from the **Baseline** facility master. In GF every `CapacityInPallet` is 0 because the company's optimized scenario deliberately removes hard capacity and fixed storage cost and charges a variable `StoragePenaltyPerPallet` instead (confirmed in company Notion). Our MILP needs fixed cost × `Y_j` and a capacity, so Baseline values are the right source. GF also lacks `FixedStorageCost_perMonth` / `MonthsPresentIn2025` (2025 history columns). Lane costs still come from GF (more lanes) | ✅ |
| 4.5 | DOS = median over product groups per facility (GF `ENO_DOS`, all 53 facilities covered): RDC ≈ 11 days, DC ≈ 10, NDC 7, DEPO 0 (cross-dock, no capacity limit) | ✅ |
| 4.6 | Demand nodes `K` = the Company's existing ship-to groups. Profile 2.4: root mapping = 34,922 ship-tos → 3,433 groups, each ship-to in exactly one group, no group spans two islands; the GF mapping is a strict subset (30,738 ship-tos, identical assignments) → **use the root mapping**. All 3,433 groups have 2025 demand (24,532 t; Java 64%). Every group is reachable from at least one of the 54 facilities; 303 groups have exactly one possible facility (their sole facility is effectively forced open unless unmet demand is allowed — handle in the model). Profile 2.4f: 3,135 t of these is one large Java group served only by the NDC (always open, no issue); the rest (~1,730 t, ~7%) sit mostly in remote areas: all 86 Malaysian groups depend on `MWH_M04`, plus Sulawesi (87 groups), Maluku, Papua, eastern Java via `MWH_D12`. Main sole-source facilities: `MWH_M04`, `MWH_D40`, `MWH_D12`, `D44`, `MWH_D39`, `MWH_D22`, `MWH_D17`  **After excluding Malaysia (2.1): 3,347 groups** (86 Malaysian groups dropped) | ✅ |

## 5. Data cleaning rules (rerun from raw data)

| # | Decision | Status |
|---|---|---|
| 5.1 | **Demand = ordered quantity (unconstrained demand), de-duplicated.** Cancelled orders count as demand (customers wanted the goods), but a cancelled picking that was re-picked as Done under the same order line must not be counted twice. Rule: rows with a real `SOLineID` → one value per (`SOLineID`, `ShipToID`, `ProductID`) = max `QtyOrderedInKG` across its pickings; rows with `SOLineID = "NULL"` (3.59M rows, cannot be de-duplicated) → Done rows only. Profile 2.5: 28,308 t over Jan–Nov (vs 24,532 t delivered, 29,509 t if all rows were summed). Including the NULL cancelled rows would add 261 t (0.9%), excluded to avoid possible double counting | ✅ |
| 5.2 | Quantity field: `QtyOrderedInKG` (see 5.1). Fill rate on Done rows is stable at 97.6–99.2% per month | ✅ |
| 5.3 | Drop rows with non-positive ordered quantity (1,029 rows) and exact duplicate rows (21 rows) | ✅ |
| 5.4 | Product master (5,174 products, no duplicate IDs, every product sold B2B is in the master). `KGPerPallet` is derived as `GrossWeightInGram × QuantityPiecesPerPallet / 1000`, so errors sit in those source columns: 302 products < 10 kg/pallet (implausible unit weights, e.g. 0.7 g) and 212 > 2,000 kg/pallet (more than a physical pallet holds). **Drop the 514 flagged products: 1.21% of delivered B2B kg** (Beauty 0.71%, Personal Care 0.50%). Dropping is preferred over imputing because the low-weight errors would otherwise inflate pallet demand many-fold. No segment filter needed: Lifestyle, Health & Wellness and blank-segment products have 0% of B2B kg | ✅ |
| 5.5 | Customer master: clean structure (48,001 rows, no duplicate IDs, Type / island / country consistent). 3 missing coordinates (all B2C cities). 28 B2B ship-tos have coordinates on the wrong island (geocoder fallbacks to a few default points, e.g. Surabaya, Jakarta), plus 5 shared coordinates used by 3+ cities. **The 28 wrong-island ship-tos carry 0 t of 2025 B2B demand**, so no coordinate fix is needed; ship-tos without demand drop out at aggregation anyway. Re-check if the demand rule (5.1/5.2) changes | ✅ |
| 5.6 | Keep B2B ship-tos present in the ship-to group mapping (all islands). Profile: every ship-to with orders exists in the customer master; 67 ship-tos with orders have no group but carry only 0.1 t (≈0%) → dropped. The 12,430 master ship-tos without a group are essentially the 12,363 with no 2025 orders (inactive) | ✅ |
| 5.7 | Cost tables: use the GF / Unconstrained scenario for transfer and last-mile (free-flow cost, not forced to historical routes); Baseline tables are forced flow and used only for comparison. Filter both origin and destination to the in-scope facilities (4.2) and demand nodes. Last-mile B2B = union of the GF and root `_Unconstaint` files (identical prices on shared lanes; root file adds 6,104 lanes from existing facilities, GF adds 15). **All GF lane costs are deflated to 2025** with the company's own factors: supply and transfer ÷ 1.1546, last-mile B2B ÷ 1.3280 (verified exact for last-mile: GF = Baseline × 1.328 on every shared lane). Keeps all costs on the same 2025 basis as demand and fixed costs | ✅ |
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

- [x] ~~Lead-time table missing~~: `LeadTime_AllFlow.parquet` added to `Raw Data/` (293,161 lanes, includes distance for every lane). Still to check: its keys match facility / ship-to group IDs of the cost tables.
- [x] ~~Questions to the company~~: answered via company Notion (2026-10-04). B2C mapping does not exist (B2C dropped, 2.2); unknown facility codes are mostly B2C facilities (no impact, demand is assigned by ship-to); two last-mile files resolved by data (5.7); `MWH_M02` → `MWH_M04` (4.2b).
- [x] ~~2030 vs 2025 cost basis~~: deflate to 2025 (5.7).
- [x] Profile 2.9a: on 3,549 shared lanes, GF = Baseline × 1.328 exactly (5–95% band 1.328–1.328), and the root `_Unconstaint` file = GF exactly on 16,748 shared lanes. So both unconstrained files are the 2025 Baseline rates uniformly inflated to 2030; dividing by 1.328 recovers 2025 rates exactly.
- [x] Two last-mile B2B unconstrained files (2.9b): the root file has 6,104 extra lanes, all from existing active facilities (DEPO 4,460, DC Direct 638, RDC 531, DC Satellite 475). GF has 74 lanes not in the root file: 59 from greenfield sites (excluded anyway) and 15 from existing DC Satellites. Prices identical on shared lanes. **Decision: last-mile B2B = union of both files, keep lanes whose origin is an existing facility, divide by 1.328 to get 2025 rates.**
- [x] ~~B2C~~: dropped (2.2).
- [x] ~~Watch item: Malaysian DC handling cost~~: moot, Malaysia excluded (2.1).
- [x] Facility master exported: `Model - Data used/facility_master.parquet`, re-exported without Malaysia → 53 facilities (1 FIXED NDC + 52 DECISION).
- [ ] Choose `L_max` (candidate: company service levels, Java within 1 day, outer Java within 3 days).
- [x] Exported to `Model - Data used/` (Indonesia only): `customer_master` (46,461), `product_master` (4,660), `facility_master` (53), `shipto_group_map` (34,430 ship-tos → 3,347 groups), `so_b2b` (24,084,062 rows, 26,790 t ordered after de-duplication, product and Malaysia filters).
- [x] Network tables exported (`Coding notebook/Validation_2_Network.ipynb`): `cost_supply` (4 lanes, cost 0), `cost_transfer` (369 lanes, 2025 basis), `cost_lastmile_b2b` (14,770 lanes, every group served, 2025 basis), `dos` (53), `lead_time` (15,139 lanes = all transfer + last-mile lanes, incl. distance; 154,217 exact duplicate rows dropped from the raw file; 424 lanes have a sea leg). After dropping Malaysia, 217 groups have a single possible facility.
- [x] ~~Confirm 5.1 and 5.2~~: demand = de-duplicated ordered quantity (2026-10-04). Re-check 5.5 / 5.6 figures (computed on delivered kg) when the demand table is built.
- [ ] Agree the trade-off definition (2.6) with the company contact.
- [ ] Build the anonymization map (facility, customer group and product labels) and apply it to every output before sharing.
- [ ] Decide `Γ` range and AUGMECON2 grid size.
- [ ] Remove the company-named files from the public GitHub repository, or make the repository private.

## 8. Change log

| Date | Change |
|---|---|
| 2026-10-06 | Title subtitle changed to "An Indonesian Case Study" (1.1) |
| 2026-10-06 | Lane sets (4.3): main run keeps the company's transfer and last-mile lane sets; their completeness is tested as a sensitivity after `f1` is solved (Backlog §2). Diagnostic cells 2.8c, 2.8d, 2.12c added to `Validation_2_Network.ipynb` |
| 2026-10-04 (night) | Malaysia excluded (2.1): Malaysian customers, ship-to groups, sales orders and the Malaysian DC are dropped; facility set becomes 53 (1 NDC + 52 decisions). Items about the Malaysian DC (4.2b, handling watch item) become moot |
| 2026-10-04 (evening) | B2C excluded (2.2). All lane costs deflated to 2025 (5.7). Last-mile B2B = union of both unconstrained files. Demand stays 2025 actuals, no forecast (2.4). Company questions closed |
| 2026-10-04 (later) | Scope widened to the full network (2.1). B2C pending (2.2). No Batang (4.1a). Candidate set = existing facilities only; 71 greenfield sites excluded (4.2, 4.2a). Capacity / fixed cost from Baseline (4.4a). Questions for the company listed in §7 |
| 2026-10-04 | Log rewritten. Topic approved. `f2` switched to lead-time coverage. Data pipeline to be rerun from raw files. Repository folders reorganized (`Document/`, `Raw Data/`, `Notebook/`) |
