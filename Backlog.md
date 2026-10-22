# Backlog — KLTN Thesis: Distribution Network Design (MOO-MCDM)

**Purpose:** Contingency items and optional extensions to revisit once modeling/data work goes deeper — checked periodically so scope issues get caught early instead of being patched around indefinitely.

---

## 1. Re-check scope fit: B2C inclusion (added 2026-09-14, updated 2026-10-04)

**Why this is here:** the scope is now the full network, B2B only (see `Decision_Log.md` §2). B2C was dropped because B2C demand cannot be placed on cities with the data available. If results only make sense with B2C included (e.g. a large share of a region's volume is B2C), the fix should be to **re-open the scope decision** (request the company's city-level e-commerce file), not to patch the data.

**Trigger conditions:**
- Coverage (f2) or CO2 (f3) results look distorted because B2C volume is missing in a region.
- B2B-only data leads to validation issues that only make sense once B2C activity is accounted for.

**Status:** not triggered. Watch item, not an active task.

---

## 2. Option: estimate last-mile B2B cost for every facility × demand-group pair (added 2026-10-04)

**Why this is here:** the company's cost tables only contain the lanes the company judged realistic (each demand group reachable from 2–7 of the 54 facilities, 303 groups from only one). For a more objective model, the user wants the option of a **full 54 × 3,433 cost matrix**, so the candidate lanes are not limited by the company's own lane selection.

**Method (best practice for estimating missing lanes):**
1. **Distance:** use real road / sea distance (`DistanceInKM` from `LeadTime_AllFlow.parquet`, OSRM-based) for every pair it covers; for pairs it does not cover, use Haversine × a circuity factor calibrated on pairs that have both.
2. **Cost function fitted on observed lanes:** regress the observed 2025 cost per pallet (company lanes, deflated ÷ 1.328) on distance, with a fixed + variable-per-km structure (`cost = a + b × km`), plus region / island and urban dummies; consider a log or piecewise form, since cost per km falls with distance.
3. **Sea legs:** cross-island pairs need a separate component (port distance and sea rate), not the road formula.
4. **Validate:** hold out ~20% of observed lanes, predict them, report MAPE. Accept only if the error is small.
5. **Merge and flag:** observed cost where it exists, estimated cost elsewhere, with an `IsEstimated` column.
6. **Sensitivity check:** solve the model with observed lanes only and with the full matrix; report whether the network and Pareto front change.

**Trade-offs to keep in mind:**
- Common practice in network design is to keep a candidate-lane set (k-nearest facilities, distance or lead-time threshold, same island) rather than the full matrix; a full matrix mostly adds lanes the optimizer never uses and increases model size (54 × 3,433 ≈ 185k last-mile arcs vs ~22k now).
- Estimated costs are a modeling assumption that must be defended; the observed-lanes-only run is the baseline.

**Transfer lanes too (added 2026-10-06):** the 369 transfer lanes are also a filtered candidate set (no complete intra-island matrix; Java alone would have 22 × 21 = 462 pairs). Option: regenerate missing facility pairs with the company's documented mid-mile formula (Assumption §5.2: DC → DC rate per pallet-km by destination island × OSRM distance × island adjustment factor × 1.1546), after first checking that this formula reproduces the existing 369 lanes. Gaps: no published rate for Maluku, Sumatra split into North / Central / South, NDC first-mile heatmap not published.

**When to trigger (decided 2026-10-06: run the model first, decide after):** after `f1` is solved, check (a) how many facilities are kept open only because they are the sole facility of one of the 217 single-source groups, (b) whether cost is sensitive to the transfer lane set (cell 2.8d), (c) whether the lead-time table has distances for missing pairs (cell 2.12c). Extend lanes only if (a) or (b) shows a material effect, and report it as a sensitivity analysis.

**Status:** activated 2026-10-09 for last-mile (`Decision_Log.md` 4.3a). Transfer lanes still the Company's 369.

---

## 3. Option: robust demand (Bertsimas & Sim) (added 2026-10-09)

**Why this is here:** the robust layer was dropped on 2026-10-09 (`Decision_Log.md` 1.3) because the Bertsimas & Sim counterpart (dual variables, budget `Γ`, price-of-robustness scan) adds too much complexity for the thesis scope. The model now uses the nominal demand `d_k` only; the demand sensitivity (+10%, +20%) was also dropped on 2026-10-17 (`Decision_Log.md` 6.1).

**Already available if it is reopened:** `d̂_k` (max − mean per group, Σ`d̂` = 65% of mean monthly demand) and the evidence that groups peak in different months (national peak only +20% over the mean, 5.9), which is the standard argument for a budgeted uncertainty set.

**When to trigger:** not planned. Mention demand uncertainty (robust optimization) only as a limitation and future work.

**Status:** option, not active.

---

## 4. Split the single product into a few product families (added 2026-10-09, planned 2026-10-12)

**Why this is here:** the model uses one aggregated product in pallets (`Decision_Log.md` 2.3). The Company model keeps ~141 product groups because it also optimizes production (lines, COGM), MFC eligibility, inventory opportunity cost and DOS per product group; none of these are in the thesis model, and lane / handling costs are per pallet for every product, so splitting would barely change which facilities open. Splitting into all 141 groups would make the MILP ~50–100× larger, too slow for repeated AUGMECON2 solves.

**If reopened:** split into 3–5 managerially meaningful families (e.g. fast vs slow movers by DOS, or main category), using `ProductGroupID` in `demand_b2b.parquet` and DOS per facility × product group (`ENO_DOS`). Gains: more accurate capacity (product-specific DOS) and CO2 (product-specific weight).

**When to trigger:** only after `f1`, `f2`, `f3` and AUGMECON2 run end to end on the single product, and if time allows. Otherwise mention as future work.

**Status:** planned (decided 2026-10-12: the product will be split). Not yet implemented. The model stays on one product until the current single-product chain (payoff table, AUGMECON2, TOPSIS) is stable, because the model is already complex; splitting comes after that. `Decision_Log.md` 2.3 still reads "one aggregated product" and must be updated when the split is coded.

**Update 2026-10-22:** the student's goal is the full Company product groups (124 groups with B2B demand), not 3–5 families; aggregation was only because the model got too large. A single-objective min `f1` test with 124 groups (~3.2M variables, 249k constraints) is in the last cell of `Multi-Objective Optimization.ipynb`; HiGHS loaded it but gave no result. The cell now has a `SOLVER` switch to retry with COPT (365-day trial license). Run `KIEM_TRA_1SP = True` first (must give f1 = 301.98), then `False`.

**Why now:** the personal care industry manages a wide and changing product range (dos Santos et al., 2025), so product families make capacity and CO2 more realistic. (2026-10-12: this point was removed from thesis section 2.1.1; if the split is done, Chapter 3 can introduce it there.) If the split is not done before submission, Chapter 3 must justify aggregation as standard for strategic network design and Chapter 5 must list it as a limitation and future work.

**Key point (2026-10-17):** lane cost, handling cost and lead time are per pallet and identical for every product, and `f3` already uses each group's own `TonPerPallet`. A split with no family-specific parameter gives the same result as one product. It only matters if families differ in DOS (capacity, which is rarely binding: max 89% in the cost-minimal network), tonnes per pallet (`f3` on transfers), or which facilities may stock them (e.g. slow movers only at NDC / RDC, derivable from 2025 `ENO_ShareLastMileB2B` / `ENO_ShareTransfer`, a forced-flow basis to be stated as an assumption).

**Step 0, data check before any model change:** for each candidate rule (ABC by pallet volume, recommended; `Segment`; kg per pallet) show the pallet share per family, median DOS per family × facility type, tonnes per pallet per family, and which facilities shipped each family in 2025. If families barely differ, keep one product and use this table in Chapter 3 to justify aggregation.

**Watch:** flow variables ≈ ×3 (AUGMECON2 133 min → ~6–10 h; 5 × 5 grid as fallback); capacity must switch to the inventory form `Σ_p Out_jp · DOS_jp / 360 ≤ CapacityInPallet_j · Y_j`; keep the open-link constraints aggregated; regression test (all families with the old DOS must give f1 = 301.98); anonymous family names (A/B/C); `pareto_flows` ≈ ×3 in size.

**To do when implemented:**
1. Choose the family rule (3–5 families, see "If reopened" above) and record it in `Decision_Log.md` 2.3.
2. Rebuild `d_k` per family in `Demand.ipynb` and the capacity rule with product-specific DOS (`Decision_Log.md` 4.4, 4.5).
3. Use product-specific `TonPerPallet` in `f3` (`Decision_Log.md` 3.3).
4. Re-run payoff table, AUGMECON2 and TOPSIS; refresh the files in `Model Outputs/Mẹ/`.
5. Update Chapter 3 wording so the thesis text matches the model.

~~Decided 2026-10-09: single product first.~~


---

## 5. Re-check the CO2 objective `f3` (added 2026-10-11)

**Why this is here:** the emission-minimal Pareto solution opens 52 of 53 facilities (cost 361.65 B IDR/yr, 1,875 tCO2e/yr), which looks counter-intuitive. It follows from how `f3` is built (`Decision_Log.md` 3.3, 3.5): warehouse emissions are charged per tonne handled (5.6 kg/t, DEPO 1.3 kg/t) with no fixed emission per open site, the van last mile carries the highest factor (756 g/t-km vs 360.83 mid mile and 79 first mile), and emission factors are fixed per t-km, so smaller loads after splitting volume over more sites are not penalized. Opening more sites shortens van legs and always lowers `f3` in the model.

**What to check:**
1. Split `f3` per Pareto option into transport by leg (first / mid / last mile, road vs sea) and warehousing, from `Model Outputs/pareto_flows.parquet`. Confirm the warehousing share (rough hand estimate: about 10% of `f3`, ~260 t/yr) before quoting it.
2. Re-check the emission factors and the leg assignment against the CEL CO2 note (`Document/CO2`): 360.83 for every facility → facility lane under the tiered flow (4.3d), 79 only for lanes leaving the NDC, sea share of estimated lanes.
3. Bound the effect of a fixed per-site emission: if all warehousing emissions were fixed per site (~7 t per site per year), going from 37 to 52 sites adds ~105 t vs ~640 t saved, so the direction holds. Recompute with the exact warehousing share from step 1.
4. Decide: keep `f3` as is and state the limitation in the thesis, or add a fixed per-site term (needs a sourced value and a full re-run of payoff table + AUGMECON2, ~5 h; avoid double counting with the GLEC per-tonne intensity).

**Status:** open. Decided 2026-10-11 to keep `f3` for now and re-check before writing the results chapter. Note (2026-10-17): the figures above are from the 11/10 run; in the 12/10 run (same-island RDC → Satellite) the min-`f3` solution opens 50 facilities at 329.44 B IDR/yr and 2,465 tCO2e/yr. Redo the checks on the 12/10 run.

---

## 6. Open model checks and result analyses (added 2026-10-17)

| # | Task | Re-solve? | Status |
|---|---|---|---|
| 6.1 | Explain why Cost-driven TOPSIS picks P32 (323.54) and not a cheap option (f1 spread ~14% vs f2 ~69%; top 3 scores 0.762 / 0.761 / 0.761) | No | open |
| 6.2 | Current-network run: fix the existing open facilities, optimize flows, report f1 / f2 / f3, compare with the TOPSIS picks | One solve | open |
| 6.3 | Split f1 per Pareto option: rent, transfer, last mile, handling | No | open |
| 6.4 | Cost per pallet per Pareto option; cost per tonne of CO2 avoided between options | No | open |
| 6.5 | Share of pallets within the Company SLA (Java ≤ 1 day, outer ≤ 3 days) per option, reported only | No | open |
| 6.6 | Results by island for the TOPSIS picks (open facilities, lead time, CO2) | No | open |
| 6.7 | CO2 sensitivity: van factor 756 on hub replenishment (`Decision_Log.md` 3.3) | Yes | open |
| 6.8 | Update the stale comment "×1.5 for +20% demand sensitivity" in the capacity cell and markdown (demand sensitivity dropped) | No | open |
| 6.9 | Create `Model Outputs/Mẹ/` with the 12/10 files (`dos_capacity.csv` already there) | No | open |
| 6.10 | Fill `Methodology & Result.md` with notebook-produced numbers only | No | open |
| 6.11 | Make the GitHub repository private / remove company-named files; build the anonymization map (`Decision_Log.md` §7) | No | open |
| 6.12 | Update `Data/CLAUDE.md` (still says `pyaugmecon` and 3 TOPSIS scenarios) | No | open |
