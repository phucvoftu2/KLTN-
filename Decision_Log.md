# Decision Log — KLTN Thesis: Distribution Network Design (MOO-MCDM)

**Purpose:** Running log of scope, modeling, and data decisions made during thesis preparation. Written so Claude (and the student) can resume work with full context without re-deriving prior reasoning.

**Working Title:** Trade-off Analysis in Personal Care Supply Chain Distribution Network: An Application of an Integrated MOO-MCDM Framework

**Last updated:** 2026-09-13

---

## 1. Thesis Identity & Methodology

- **Type of study:** Robust Multi-Objective Mixed-Integer Linear Programming (MOMILP) for distribution network design under demand uncertainty.
- **Optimization type:** Free/full optimization — the solver decides facility opening/closing (binary `Y_j`) itself. No forced routing shares (Paragon's own model forces shares to replicate its current network for baseline validation purposes only; this thesis does not use that pattern).
- **Solution pipeline (3 stages):**
  1. Mathematical modeling — Robust MOMILP with Bertsimas & Sim interval/budget-of-uncertainty framework (chosen over scenario-based robust optimization because it requires no probability assumptions on demand scenarios).
  2. Pareto optimization — AUGMECON2 (Mavrotas & Florios, 2013) to generate the exact non-dominated Pareto frontier.
  3. Managerial evaluation — TOPSIS to rank Pareto-optimal configurations under multiple weighting scenarios (Cost-Driven, Service-Driven, Balanced/Green).
- **Toolchain:** Python — Pyomo + pyaugmecon + HiGHS + pymcdm.
- **Reference model:** `Data Dictionary/Modeling/Model - Notion/Model.md` (Paragon's real single-objective LP network model) is used **only as a reference for how to structure the granular TotalCost formula** (Supply/Transfer/Delivery/Storage/Handling cost components). It is NOT used for its methodology — Paragon's model deliberately avoids binary open/close variables (pure LP, rule-based heuristics between runs instead) and forces routing shares for its Baseline scenario. This thesis intentionally does the opposite: true binary `Y_j` optimization, no forced shares.
- **MCDM library: `scikit-criteria`**, not `pymcdm` (superseded — confirmed live in `Model.ipynb` cell 1, which already imports `skcriteria.agg.topsis`/`similarity`; note `skcriteria.madm`, `.agg.similarity`, `.pipeline` are deprecated in favor of `.agg`/`.pipelines`). Update all references from `pymcdm` → `scikit-criteria`.

### 1.1 Build Sequencing (2026-09-13)

- **Decision: build and validate `f1` (Total Cost) alone first — single-objective MILP — before adding `f2` (Uncovered Demand) and `f3` (CO2).** Rationale: `f2`/`f3` still need more research/confirmation (coverage threshold `D_max`, geography scope, GLEC EF application details) — building `f1` first lets the data pipeline, Pyomo model structure, and robust (Bertsimas–Sim) term get implemented and debugged end-to-end on real data without being blocked on those open items.
- This is a **build-sequencing decision only**, not a scope change — the thesis remains a 3-objective Robust MOMILP (`f1`, `f2`, `f3`) solved via AUGMECON2 + TOPSIS. `f2`/`f3` will be layered into `Model.ipynb` §4.2 once their open items are resolved, before the AUGMECON2 stage (§5) is run (AUGMECON2 requires all objectives defined).
- Practical implication for `Model.ipynb`: §4 (Mathematical Model Formulation) initially implements only `f1` + its constraints (flow balance, robust demand satisfaction, capacity, linking, no-self-transfer, fixed backbone) as a single-objective `minimize` model, solved directly via HiGHS (no AUGMECON2 needed yet for one objective). §5 (AUGMECON2) and §6 (TOPSIS) stay stubbed until `f2`/`f3` are added.

---

## 2. Scope Decisions

| Dimension | Decision | Rationale |
|---|---|---|
| **Geography** | **Java-only** (CONFIRMED 2026-09-13, was Java+Sumatra) | Simplification + tractability. Factory and NDC are both already in Java, so dropping Sumatra removes all cross-island flow modeling entirely — network becomes **single-mode (truck/OSRM only)**: no sea-leg (Sunda Strait ferry) distance, no GLEC Ocean Transport EF (22.35 gCO2e/t-km) needed in f3, no port-distance columns to handle in the distance file. Also shrinks model size (fewer facilities/clusters), which matters for repeated AUGMECON2 + Γ-sensitivity solves within the KLTN timeline. Trade-off: representativeness drops from ~74.8% (Java+Sumatra, 35,904/48,001 customer records) to a lower Java-only share — documented as a stated delimitation, not a data gap. |
| **Time horizon to optimize** | 2030 (projected/optimized network) | Matches thesis goal of a forward-looking strategic recommendation. 2025 data is used only as the historical basis to calibrate demand (nominal + variability), not as the year being optimized. |
| **Channel** | **B2B only — B2C dropped entirely** | B2C data lives in a separate source system (`EcomTransaction.parquet`) with different granularity/units (no KG column, pre-aggregated by month) than B2B (`SO.parquet`, transaction-level). Dropping B2C removes this entire data-reconciliation problem, removes `DeliveryCostB2C`/`HandlingCostB2C`/B2C packaging & manpower cost terms from f1, and keeps the demand-estimation methodology consistent (one source, one method). Documented as a scope limitation, not a methodological flaw. |
| **Product** | Single aggregated product (no per-SKU/ProductID dimension) | Matches the original MOMILP formulation (Context-V1.md / thesis proposal), which has no explicit product set `p` — only sets I, J, K, M, T. Keeping multi-product would multiply model size and make the already-heavy pipeline much harder to solve within the 15-week KLTN timeline. |
| **Demand unit for aggregation** | KG (weight), not raw PCS count | Summing raw PCS across different products is not physically meaningful. KG is comparable across products. B2B's `SO.parquet` already has `QtyDeliveredInKG`/`QtyOrderedInKG`, no conversion needed. |

---

## 2.1 Supply Origin (Factory) Decision

- **No MNO (Manufacturing Network Optimization).** Factory/production side is NOT optimized — no `ProductionCost`, `LineCapacity`, `ProdMap`, or `COGM` needed. Factory acts purely as a fixed supply origin for the DNO (Distribution Network Optimization) model.
- **Baseline (current, active) factories only — 3 total, all at the Jatake industrial site:** Jatake 1 (Powder), Jatake 2 (Liquid), Jatake 4 (Semisolid). Batang and Jatake 7 excluded (future/target-network factories, out of scope since factory-opening is not a decision this thesis makes).
- **Decision: merge all 3 Jatake factories into a single Factory node ("Jatake").** They are co-located at the same physical site, and the thesis already aggregates all products into one combined demand figure, so the only thing distinguishing the 3 factories (product type) is not modeled anyway. `|I| = 1`.
- **UPDATE (2026-09-10): Factory node needs NO separate coordinate or capacity data at all.** Confirmed by inspecting `ENO_CostSupply.parquet` (real Paragon data, `DATA/06.Model_Data_Input/0,1_Baseline2025/`): Supply flow is only ever Factory → NDC (4 rows: origins J1/J2/J4/J6 → destination NDC), and `CostPerPallet = 0` for all of them — the factories and NDC Jatake are on the same site, so first-mile cost is genuinely zero, not something requiring distance-based estimation. Combined with the no-MNO decision (no production-capacity constraint to enforce), the Factory node requires **no location data** (cost is already given as a flat value, not distance-derived) and **no capacity figure** (supply is treated as unconstrained — Paragon's real total production capacity, 312M+ pieces/year, comfortably exceeds the B2B Java+Sumatra demand slice this thesis models). This item is fully closed, not merely simplified.

---

## 3. Network Structure Decisions

Based on `FacilityMaster`, filtered to Java + Sumatra: **44 total facilities**.

| Role | FacilityType(s) | Count (Java+Sumatra) | Treatment |
|---|---|---|---|
| Fixed backbone (always open, not a decision variable) | NDC | 1 (NDC Jatake 6, located in Java) | `Y_NDC` forced = 1. |
| Fixed backbone | RDC | 7 | Always open; only flow is optimized through it. |
| Fixed backbone | DC Direct | 6 | Always open. |
| Fixed backbone | DC Satellite | 10 | Always open. |
| **Y_j candidates (open/close decision)** | DEPO | 12 | Merged into one category: **"Last-Mile Facility."** |
| **Y_j candidates** | FC | 6 | Merged into "Last-Mile Facility." |
| **Y_j candidates** | Instant Hub (MFC) | 2 | Merged into "Last-Mile Facility." |
| **Total Y_j candidates** | | **20** | |

**Important clarifications resolved during discussion:**
- "LMH" (Last-Mile Hub) in the ENO network diagram is not a distinct FacilityType in the raw data — it corresponds physically to the **DEPO** FacilityType.
- All 44 facilities show `Status == "Active"` — for this thesis's true MOMILP, all facilities in the master ARE the candidate set J; `Y_j` is a new decision variable the student introduces.

**UPDATE (2026-09-14) — Candidate facility relabeling ("DEPO" as the generic B2B last-mile role):**
Per Paragon's own facility-role classification, FC and Instant Hub (MFC) are technically **B2C-serving** facility types in their original operational context — unlike DEPO, which is separately confirmed as a genuine B2B cross-dock role (§5.6). Simply calling all 20 candidates "generic" (the original framing) was logically weak for a B2B-only thesis. Resolved as follows:
- **Narrative/reporting label only:** in the thesis text (Problem Statement, model description), all 20 `Y_j` candidate facilities (DEPO=12, FC=6, Instant Hub=2 — Java+Sumatra count, pending Java-only recount) are referred to uniformly as **"Depots"** / generic B2B last-mile facility nodes — regardless of their original FacilityType label in Paragon's source system. Justification: this thesis's model does not differentiate cost or emission structure between DEPO/FC/Instant Hub in the first place — they were already merged into one f1 candidate role (this section) and one f3 EF class ("Mainly Handling", §4) before this relabeling decision, so nothing about the actual math changes.
- **Underlying data processing is NOT relabeled.** The real `FacilityType` field (DEPO/FC/Instant Hub) from `FacilityMaster` MUST still be used as-is for: (a) the Transfer arc topology in §3.1 (the 16 valid (Origin_Type, Dest_Type) combinations reference the real types — e.g. `DEPO -> Instant Hub` and `Instant Hub -> Instant Hub` are valid, `DC Satellite -> FC` is valid, but there is no `DEPO -> DEPO` arc — collapsing the real types before building `A^T` would silently break this topology), and (b) any per-facility cost/capacity lookup, which is keyed by facility ID, not by the display label. Renaming is cosmetic/narrative only, applied after all data processing is done.
- Net effect: candidate set size stays at 20 (pending Java-only recount, per Open Items), only the way it is *described* in prose changes.

### 3.1 Transfer arc topology (NEW, confirmed via `ENO_CostTransfer.parquet`)

The real network is **strictly hierarchical** (tiered), confirmed against the ENO Perimeter network diagram: flows only go top-down through tiers (NDC → RDC/DC/FC/Instant Hub → downstream), never sideways or upward. Cross-checking `ENO_CostTransfer.parquet`'s `Origin_Type`/`Dest_Type` combinations (after joining `OriginID`/`DestinationID` to `FacilityMaster`) surfaced exactly **16 valid flow types**:

```
NDC -> DC Satellite      DC Satellite -> FC          RDC -> DC Direct
NDC -> RDC                DC Satellite -> DC Satellite RDC -> DEPO
NDC -> DC Direct          DC Direct -> DEPO            DC Satellite -> DEPO
NDC -> FC                 DC Direct -> FC              DEPO -> Instant Hub
NDC -> Instant Hub        RDC -> FC
RDC -> DC Satellite       Instant Hub -> Instant Hub
```

**Modeling implication:** the sparse coverage in `ENO_CostTransfer.parquet` (only ~95 observed lanes, not a full 44×44 matrix) is NOT a data-quality gap — it reflects that most facility-type pairs are operationally invalid. The candidate arc set for the `Transfer[fl,fl2]` decision variable should be restricted to pairs whose `(Origin_Type, Dest_Type)` combination appears in the 16 above, rather than allowing all J×J pairs. This is both operationally realistic and reduces model size (fewer arcs/variables) — good for AUGMECON2 + robust + Γ-sensitivity tractability.

---

## 4. Objective Functions

- **f1 — Total Cost (minimize).** Reference formula:
  ```
  TotalCost = Σ SupplyCost[fl]                                   # Factory → NDC (Supply)
            + Σ TransferCost[fl]                                  # Facility ↔ Facility (mid-mile)
            + Σ DeliveryCostB2B[fl]                                # Facility → ship-to group (last-mile B2B)
            + Σ FixedStorageCost[fl]                               # fixed DC operating cost
            + Σ StoragePenaltyPerPallet[fl] * ExcessInventoryFacility[fl]
            + Σ HandlingCostB2B[fl]
  ```
  IOC excluded. B2C cost terms removed. `FixedStorageCost[fl]` (from FacilityMaster) plays the role of `F_j · Y_j` for open/close decisions. All 3 cost-rate components (Supply/Transfer/LastMileB2B) now sourced from real data — see §5.2 below.

- **f2 — Coverage-based service level (minimize uncovered demand), MCLP-style.** NOT lead time. `minimize Σ_k D_k × (1 − covered_k)`, `covered_k = 1` if at least one open facility lies within a coverage threshold of cluster `k`. Needs: (a) distance matrix Facility↔Cluster — **RESOLVED, see §5.7**: use the real `DistanceInKM` field from `All_Flows_FMM_LM_Indo_Malay_With_Distance.parquet` (actual OSRM road routing + sea-leg distance), NOT self-computed Haversine. (b) coverage threshold — **still open**, candidate: Paragon's own SLA (Java ≤150km/1 day, outer Java ≤500km/3 days), not yet confirmed by student. (c) binary coverage matrix — derivable once (a) and (b) are set.

- **f3 — CO2 Emissions (minimize).** **RESOLVED (2026-09-10)** — full methodology and emission factors sourced from Paragon's real GLEC-based Environmental Impact assessment (`CO2.md`, `PRGNENO_Environmental_Impact.md`, GLEC Framework PDF — all internal CEL documents on the ENO project). Adapted to thesis scope (DNO only, B2B only, no automation):

  ```
  CO2e (transport, per flow) = Volume (tonnes) × Distance (km) × EF (gCO2e/tonne-km)
  CO2e (warehousing, per facility) = Outbound throughput (tonnes) × Warehouse EF (kgCO2e/tonne)
  ```

  | Flow in this thesis's model | GLEC category | EF | Notes |
  |---|---|---|---|
  | Supply (Factory→NDC) | First Mile | 79 gCO2e/t-km | Distance ≈0 (co-located) → contribution negligible |
  | Transfer (Facility→Facility, not final leg) | Mid Mile | 360.83 gCO2e/t-km | |
  | LastMileB2B, origin = NDC | Last Mile B2B – Direct | 79 gCO2e/t-km (uses First Mile EF) | |
  | LastMileB2B, origin ≠ NDC | Last Mile B2B – Indirect | 756 gCO2e/t-km | |
  | Warehousing — DEPO/FC/Instant Hub ("Last-Mile Facility" / Y_j candidates) | Mainly Handling | 1.3 kgCO2e/tonne | Maps directly onto existing facility classification (§3) |
  | Warehousing — NDC/RDC/DC Direct/DC Satellite (fixed backbone) | Storage + Handling | 5.6 kgCO2e/tonne | |

  **Explicitly excluded from thesis f3** (present in Paragon's full model but out of this thesis's scope): Production/Manufacturing emissions (no MNO), Automation electricity scenario (not modeled), Last Mile B2C / Instant Delivery (B2C dropped), Ocean Transport EF 22.35 gCO2e/t-km (only needed if Sumatra — i.e. inter-island — flows are kept; see Open Items re: Java-only).

  **Data needed — all reused from data already sourced for f1/f2, nothing new required:**
  - Volume: same flow decision variables as f1, converted tonnes = KG / 1000.
  - Distance: same real distance field (`DistanceInKM`) sourced for f2 coverage — see §5.7. GLEC's own methodology already bakes in a routing-inefficiency factor on top of shortest-feasible-route; since `DistanceInKM` here is real OSRM/sea-routing distance (not a straight-line estimate), the extra ×1.05 detour factor is optional/minor — can be applied for stricter alignment with GLEC convention or skipped as immaterial, student's call.
  - EF constants: the 5 values above, cited directly to the **GLEC (Global Logistics Emissions Council) Framework** — a public, citable methodology (not proprietary Paragon data), so safe to reference academically.

---

## 5. Demand Data — Source & Methodology

### 5.1 File lineage discovered (via Notion)

**B2B pipeline:**
`01.Data_from_client/Transactional Data/Raw_SO_*.parquet` → cleaned by `PRGN.Clean_SalesOrder.Rmd` → **`02.Cleaned_data/SO.parquet`** (26,888,720 rows × 27 cols, Jan–Nov 2025 real data). Sub-extract used: **`B2B_SO_2025_JantoNov.parquet`** (B2B-only, Jan–Nov 2025).

Downstream, NOT used (extrapolated/model-derived): `SO_2025_FullYear.parquet` → `SO_2025_FullYear_With_Value.parquet` (fills Dec 2025 via a growth-rate "black box" model).

**B2C pipeline** (discovered, NOT used — B2C out of scope): `EcomTransaction.parquet`, `B2C_SO_2025_JantoNov.parquet`.

### 5.2 Final decision: which file to use

**Use `DATA/02.Cleaned_data/B2B_SO_2025_JantoNov.parquet` only**, for both:
- **d̄_k (nominal annual demand):** `(sum of 11 real months ÷ 11) × 12`.
- **d̂_k (deviation/uncertainty budget input):** month-to-month variability across the 11 real months.

Why not the pre-built "FullYear" extrapolated files: (a) Dec is model-generated, not real, biasing variance; (b) extrapolation methodology is a black box; (c) one raw source + one defensible method is methodologically cleaner.

### 5.3 Why demand must be annualized

All cost data in FacilityMaster is annual. Leaving demand at an 11-month raw total while fixed costs represent a full year would systematically overstate "fixed cost per unit of throughput," biasing `Y_j` toward closing facilities more than optimal. Annualizing (×12/11) removes this bias.

### 5.4 Demand clustering (K) — RESOLVED (2026-09-10)

**Decision: reuse Paragon's existing 3,433 ship-to groups as the demand cluster set `K`, instead of building custom K-medoids clustering.**

Evidence chain that confirmed this:
1. `ENO_CostLastMileB2B.parquet` (`DATA/06.Model_Data_Input/0,1_Baseline2025/`, 3,635 rows: OriginID, DestinationID, CostPerPallet) has `n_distinct(DestinationID) = 3433` — exact match to the "34,922 B2B ship-to → 3,433 groups" figure from the PRGN ENO project-context doc.
2. `ENO_DemandAllocationB2B.parquet` (same folder, 5,835,102 rows: ShipToGroupID, ProductGroupID, ShipToID, ProductID, DemandInPCS, Ratio) confirmed `n_distinct(ShipToGroupID) = 3433` and `n_distinct(ShipToID) = 34922` — exact match again.
3. Verified the mapping is clean many-to-one: `DemandAlloc %>% distinct(ShipToID, ShipToGroupID) %>% count(ShipToID) %>% filter(n>1) %>% nrow()` → **0**. Every ship-to belongs to exactly one group — no fractional/split allocation to worry about.

**Why this is better than building custom clustering:** the cost data (`CostLastMileB2B`) is already computed and keyed at exactly this group granularity — reusing it means zero cost-estimation error for known lanes, and no need to justify a from-scratch clustering methodology (K-medoids parameter choices, weighting scheme, etc.) in the thesis defense.

**How to use it:** take distinct `(ShipToID, ShipToGroupID)` pairs from `ENO_DemandAllocationB2B.parquet` → join onto `B2B_SO_2025_JantoNov.parquet` by `ShipToID` → aggregate demand (KG) by `ShipToGroupID` to get `d̄_k`, `d̂_k` for k = 1..3433 (subset to whichever groups fall inside the Java(+Sumatra) scope).

### 5.5 Cost-rate data (Supply / Transfer / LastMileB2B) — RESOLVED (2026-09-10)

All 3 lane-level cost tables needed for f1 (previously the #1 open item) were located at **`DATA/06.Model_Data_Input/0,1_Baseline2025/`** (the "Baseline 2025" scenario input folder — this is the general path pattern for all `ENO_*.parquet` scenario files):

- **`ENO_CostSupply.parquet`** (4 rows) — Factory→NDC, `CostPerPallet = 0` for all (co-located; see §2.1).
- **`ENO_CostTransfer.parquet`** (95 rows) — Facility→Facility; sparse but explained by the strict tiered topology (§3.1), not a data gap.
- **`ENO_CostLastMileB2B.parquet`** (3,635 rows) — Facility→ship-to group (3,433 destinations, see §5.4); this is where the ship-to-grouping discovery came from.

**Methodology behind these rates** (from Paragon's own Notion documentation, for context/defensibility, not required to replicate exactly):
- SupplyRate: a "heatmap" of cost/pallet from NDC to each destination city/district, from historical cost or Paragon's rate card, outlier-smoothed, with a **2.92%/year inflation factor** (~15.46% over 5 years) to project to 2030.
- TransferRate: weighted-average **IDR/pallet-km** by flow type (DC→DC, DC→FC, DC→Last-mile Hub, Last-mile Hub→MFC), varying by island (Java DC→DC: 2,065–3,769 IDR/pallet-km), same inflation factor.
- B2BRate/LastMileB2B: historical shipment cost/pallet-km by destination, with its own **5.84%/year inflation** (~32.80% over 5 years, higher than First/Mid Mile because driver cost — tied to minimum wage — is a bigger share).

**Decision on inflation-to-2030:** NOT replicated in this thesis (the full heatmap + outlier-smoothing + inflation pipeline requires internal Assumption Document data the student doesn't have access to and would be disproportionate effort for a KLTN). Thesis uses the given `CostPerPallet` values as-is (2025 basis), documented as a stated limitation/simplification, OR a simple flat inflation index can optionally be applied — **still an open decision**, see Open Items.

**On missing lanes:** since `CostTransfer` doesn't cover all valid (per §3.1) facility pairs, missing lanes should be estimated as `average_rate (IDR/pallet-km, derived from the existing ~95 observed lanes) × Haversine distance`, rather than trying to replicate Paragon's exact rate-card methodology.

### 5.6 DOS (Days of Supply) — RESOLVED (2026-09-10)

Needed only if f1 keeps the `StoragePenaltyPerPallet × ExcessInventoryFacility` term (inventory = Outbound × DOS/360). Found at `DATA/06.Model_Data_Input/0,1_Baseline2025/ENO_DOS.parquet` (5,969 rows: LocationID, ProductGroupID, DOS).

- Since the thesis aggregates to 1 product, DOS must be aggregated to 1 value per facility. **Use median, not mean** — `summary(DOS$DOS)` showed Mean = 183.2 days vs Median = 29.8 days, with Max = 58,237 days (an extreme outlier skewing the mean); median is far more representative of real warehouse operations.
- Coverage check against the 44-facility Java+Sumatra scope: 12 facilities missing — **all 12 are DEPO** facilities. Interpreted as expected, not a data gap: DEPO = LMH, a cross-dock/last-mile hub that doesn't hold meaningful inventory (§3, DEPO confirmed B2B-only cross-dock role) → **DOS = 0 for all 12 DEPO facilities** (documented assumption). The other 17 IDs present in `ENO_DOS.parquet` but outside scope (D66/D72/D78/D79/D81, all `MWH_*`) belong to other islands or to Paragon's future/optimized-network naming convention — irrelevant, ignored.

### 5.7 Distance & Lead-Time Data — RESOLVED (2026-09-10)

**Decision: use Paragon's real, pre-computed distance data instead of self-built Haversine.** Found via `CO2.md`'s data-sources section (`DATA/03.Summarized_data/`):

- **`All_Flows_FMM_LM_Indo_Malay_With_Distance.parquet`** (51,388 rows, 28 cols) — distance for lanes that exist in Paragon's current network. Key columns: `FlowType`, `OriginID`, `DestinationID`, `OSRMDistanceInKM` (real road-routing distance via OSRM, not straight-line), `SeaDistanceInKM` + `OriginToPortDistanceInKM` + `PortToDestinationDistanceInKM` + `OriginPortName`/`DestPortName` (for inter-island sea legs), `DistanceInKM` (final combined distance — use this directly), `DistanceType` (flags OSRM-only vs Non-OSRM/sea-involving routes).
- **`All_Non_Existing_Flows_FMM_LM_Indo_Malay_with_distance.parquet`** — same structure, for lanes NOT in Paragon's current baseline (candidate/new lanes). **Not yet opened/validated** — needed because this thesis's `Y_j` is free to open facilities Paragon's current network doesn't route through, so candidate-lane distances will likely be required from here.
- **`LeadTime_FirstMid_B2BLastMile.parquet`** — not yet opened; likely covers First/Mid-Mile distance or lead-time explicitly (the "existing flows" file above does not have a distinct "First Mile" `FlowType` label).

**`FlowType` values found (after excluding B2C) and their mapping to this thesis's model:**

| FlowType | Rows (full Indo+Malay) | Rows (Java+Sumatra origin only) | Maps to |
|---|---|---|---|
| DC to Customer | 41,079 | 19,886 | LastMileB2B — Indirect (origin ≠ NDC) |
| DC to DC | 819 | 276 | Transfer |
| NDC to DC | 63 | 63 | Transfer |
| NDC to Customer | 1 | 1 | LastMileB2B — Direct (origin = NDC) |
| FC to B2C City | 9,426 | — | Excluded (B2C, out of scope) |

Notable: `NDC to Customer` has only **1 row** — matches the ENO Perimeter diagram's own annotation ("Watsons is the only case of direct customer delivery from the NDC"), confirming the data is internally consistent, not a defect. This also means the f3 "Last Mile B2B – Direct" EF category is a near-edge-case in the real historical baseline, though it remains structurally available in the model.

Coverage after filtering to Java+Sumatra origins (via join to `FacilityMaster.LocationID`/`MainIsland`): **20,226 usable rows** (DC to Customer + DC to DC + NDC to DC + NDC to Customer).

**Use of `DistanceInKM` going forward:**
- f1: for `Transfer`/`LastMileB2B` lanes missing from `ENO_CostTransfer`/`ENO_CostLastMileB2B` (§5.5), estimate cost as `average observed rate (IDR/pallet-km) × DistanceInKM` instead of a Haversine-based estimate.
- f2: coverage matrix built directly from `DistanceInKM` against the (still-open) SLA threshold.
- f3: `DistanceInKM` plugged directly into the CO2e transport formula.
- Supply (Factory→NDC) is NOT covered by this file — not needed, since that leg's cost is already a flat 0 (§2.1, §5.5) and requires no distance.

---

## 6. Data Quality Validation Results

### CustomerMaster_DetailedLevel.parquet — **PASS**
- Total: 48,001 rows. NA coordinates: 3. Duplicate LocationID: 0.
- `MainIsland`: Java (26,459), Sumatra (9,445).
- After filter + drop NA coords: 35,630 B2B / 273 B2C (B2C dropped per §2).
- District column: 3,861 distinct districts (used only as a sanity cross-check against the 3,433 ship-to groups — confirmed to be a different, demand-weighted grouping, not raw districts, per §5.4).

### FacilityMaster.parquet — **PASS**
- 67 facilities total, all `Status == "Active"`.
- Filtered to Java+Sumatra: 44 total (§3 breakdown).
- Contains near-complete per-facility cost columns for f1 (`FixedStorageCost`, `B2BPackagingCostPerPallet`, `B2BManpowerCostPerPallet`, `B2BHandlingCostPerPallet`, `StoragePenaltyPerPallet`).
- `MonthsPresentIn2025` — prefer `FixedStorageCost_perMonth × 12` for facilities active <12 months, for full-year consistency (§5.3 principle).

### B2B_SO_2025_JantoNov.parquet — structure validation still pending (not blocking; file confirmed real, Jan–Nov 2025 coverage, 2GB on disk, loads fine via Arrow lazy evaluation).

### ENO_CostSupply.parquet — **PASS** (4 rows, Factory→NDC, cost=0 as expected — see §2.1, §5.5)

### ENO_CostTransfer.parquet — **PASS with caveat** (95 rows; sparse coverage explained by hierarchical topology, not a data defect — see §3.1)

### ENO_CostLastMileB2B.parquet — **PASS** (3,635 rows; DestinationID confirmed = ship-to group ID, not raw district — see §5.4)

### ENO_DemandAllocationB2B.parquet — **PASS** (5,835,102 rows; clean 1:1 ShipToID→ShipToGroupID mapping verified, 0 ship-to belongs to >1 group — see §5.4)

### ENO_DOS.parquet — **PASS with adjustment** (5,969 rows; use median not mean due to extreme outliers; 12 DEPO facilities set to DOS=0 by assumption — see §5.6)

---

## 7. Open Items / Not Yet Decided

- [x] ~~Geography: narrow Java+Sumatra down to Java-only?~~ — **CONFIRMED 2026-09-13** (see §2). **Follow-up action (not yet done):** recount Java-only facility/candidate/customer numbers (currently only have the Java+Sumatra combined 44 facility / 20 candidate breakdown in §3, and the CustomerMaster split in §6) — requires re-running the R validation scripts filtered to `MainIsland == "Java"` only. Also recheck §5.4 (K, demand clusters) and §5.7 (distance file) row counts restricted to Java-only.
- [ ] Coverage threshold (distance/time) for f2 — candidate: Paragon's own SLA (Java ≤150km/1 day, outer Java ≤500km/3 days), found in PRGN ENO project-context doc but not yet confirmed by student as the value to adopt.
- [ ] Uncertainty budget Γ — not yet chosen; sensitivity analysis planned, starting range TBD.
- [ ] Inflation-to-2030 for cost rates (SupplyRate/TransferRate/B2BRate currently on a 2025 basis) — decide whether to apply a simple flat inflation index or use as-is with a documented limitation (see §5.5).
- [ ] Final structural validation of `B2B_SO_2025_JantoNov.parquet` itself (columns, OrderStatus filter, row count) — in progress, not blocking.
- [ ] Open and validate `All_Non_Existing_Flows_FMM_LM_Indo_Malay_with_distance.parquet` (candidate-lane distances, needed because `Y_j` may open facilities outside Paragon's current baseline routing) and `LeadTime_FirstMid_B2BLastMile.parquet` (§5.7) — not yet opened.
- [x] ~~Distance matrix (Facility↔Facility, Facility↔ship-to)~~ — **resolved** (§5.7): real OSRM/sea-routing distance found (`All_Flows_FMM_LM_Indo_Malay_With_Distance.parquet`), replaces the planned self-built Haversine matrix; used for f1 (missing-lane cost estimate), f2 (coverage), and f3 (CO2 distance) alike.
- [x] ~~Factory/Plant master data~~ — **fully resolved** (§2.1): single "Jatake" node, no coordinates or capacity data needed at all (cost already given as flat 0; supply treated as unconstrained since no MNO).
- [x] ~~Lane-level cost matrices (SupplyRate, TransferRate, B2BRate/LastMileB2B)~~ — **resolved** (§5.5): all 3 found at `DATA/06.Model_Data_Input/0,1_Baseline2025/`.
- [x] ~~CO2 emission factors (f3)~~ — **resolved** (§4, f3 section): full GLEC-based methodology and all 5 needed EF constants sourced from Paragon's own Environmental Impact documentation.
- [x] ~~Weighted clustering method for demand points~~ — **resolved** (§5.4): reuse Paragon's existing 3,433 ship-to groups, mapping file found and verified clean.
- [x] ~~DOS data~~ — **resolved** (§5.6): found, median aggregation, DEPO=0 assumption documented.

---

*This log should be updated whenever a new scope, modeling, or data-source decision is made — treat it as the single source of truth for "what have we already decided," to avoid re-litigating settled questions.*
