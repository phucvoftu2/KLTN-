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

**Status:** option, not active. Main pipeline uses the company's lane costs (`Decision_Log.md` 5.7). Consider as a sensitivity analysis if time allows.
