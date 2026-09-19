# Methodology & Result

**KLTN Thesis — Trade-off Analysis in Personal Care Supply Chain Distribution Network: An Application of an Integrated MOO-MCDM Framework**

**Status:** Draft for alignment — review before code implementation. Companion to `Decision_Log.md` and `Data_Dictionary.xlsx`. **Last updated: 2026-09-13** (added §4 Product Aggregation Assumption, §5 Robust Demand Aggregation; resolved pallet/tonnes unit consistency; resolved time-horizon — model built directly on observed 11-month period, no extrapolation/annualization; resolved $\hat d_k$ formula — standard deviation, based on empirical comparison against max-minus-mean).

---

## 1. Problem Statement

Design the 2030 distribution network of a personal care FMCG company across **Java** (single-mode, truck/road transport only) by deciding which candidate last-mile facilities to open, and how to route product from a single factory source through the network to B2B demand clusters, so as to simultaneously minimize total cost, minimize uncovered demand, and minimize CO2 emissions, under demand uncertainty — using a robust, capacitated, multi-objective mixed-integer linear program (MOMILP).

---

## 2. Sets and Indices

| Symbol | Definition | Cardinality |
|---|---|---|
| $i \in I$ | Factory / supply origin (3 Jatake plants merged into 1 node) | $\lvert I \rvert = 1$ |
| $j, l \in J$ | Facility node | $\lvert J \rvert$ = **TBD, Java-only recount pending** (was 44 for Java+Sumatra) |
| $J^{B} \subset J$ | Fixed-backbone facilities (NDC, RDC, DC Direct, DC Satellite) — always open | **TBD** (was 24 for Java+Sumatra) |
| $J^{C} \subset J$ | Candidate "Last-Mile Facility" nodes — narratively referred to as **"Depots"** (underlying data spans DEPO/FC/Instant Hub FacilityTypes; relabeled for reporting only, real type preserved for arc topology — see Decision Log §3 update 2026-09-14) — open/close decision | **TBD** (was 20 for Java+Sumatra) |
| $k \in K$ | Demand cluster (B2B ship-to group, reused from Paragon's 3,433 pre-built groups, subset within scope) | $\lvert K \rvert \le 3{,}433$ |
| $(j,l) \in A^{T} \subseteq J \times J$ | Valid Transfer arc — restricted to the 16 (OriginType, DestType) combinations observed in the real network hierarchy | 16 type-pairs |
| $(j,k) \in A^{D} \subseteq J \times K$ | Valid LastMileB2B arc (facility → cluster) | per `ENO_CostLastMileB2B` + distance-estimated lanes |
| $w \in W$ | MCDM weighting scenario for the post-optimization TOPSIS stage: {Cost-Driven, Service-Driven, Balanced/Green} | 3 |

**Time horizon:** single period, static network design. Demand and flow parameters are built directly on the **observed 11-month period (January–November 2025)** — the full extent of available transactional data — used as-is, with **no extrapolation of a 12th month and no annualization/annual-equivalent reporting at any stage** (see §5). No index $t$ — this thesis does not model multi-period/temporal dynamics (matches Paragon's own model scope).

---

## 3. Parameters

| Symbol | Description | Source |
|---|---|---|
| $\text{SupplyRate}$ | Factory → NDC cost rate (IDR/pallet) | `ENO_CostSupply` — all = 0 (co-located) |
| $\text{TransferRate}_{j,l}$ | Facility → Facility cost rate (IDR/pallet), $(j,l) \in A^{T}$ | `ENO_CostTransfer`; missing arcs estimated via avg. rate × `DistanceInKM` |
| $\text{B2BRate}_{j,k}$ | Facility → cluster cost rate (IDR/pallet), $(j,k) \in A^{D}$ | `ENO_CostLastMileB2B`; missing arcs estimated via avg. rate × `DistanceInKM` |
| $\text{FixedStorageCost}_j$ | Fixed operating cost of facility $j$ — native granularity (full-year contractual vs. period-actual) and period-consistency with the 11-month model horizon (§2) not yet confirmed, see Open Items | `FacilityMaster` (× 12/`MonthsPresentIn2025` if <12 months active — **pending review**) |
| $\text{HandlingCostB2B}_j$ | Manpower + packaging rate per pallet at $j$ | `FacilityMaster` |
| $\text{StoragePenaltyPerPallet}_j$ | Penalty rate for inventory exceeding capacity | `FacilityMaster` |
| $\text{DOS}_j$ | Days of Supply at facility $j$ (median across product groups; DEPO = 0) | `ENO_DOS` |
| $\text{Cap}_j$ | Usable pallet capacity, $= \text{CapacityInPallet}_j \times 0.85$ (85% practical-utilization assumption) | `FacilityMaster` |
| $\text{Dist}_{j,l}$, $\text{Dist}_{j,k}$ | Real distance (km) — road (OSRM) and/or sea-leg combined | `Distance_LeadTime.DistanceInKM` |
| $\bar d_k$ | Nominal **pallet-equivalent** demand at cluster $k$ over the observed 11-month period (Jan–Nov 2025), $= \text{sum of pallet-equivalent demand across the 11 real months}$ — used directly, **no annualization or extrapolation**, computed on the aggregate (post-SKU-conversion) series — see §4, §5 | `b2b_so` × `ProductMaster` (SKU→pallet conversion), aggregated via `ENO_DemandAllocationB2B` mapping |
| $\hat d_k$ | Demand deviation at cluster $k$, $= \text{standard deviation of the monthly aggregate pallet-equivalent series at } k$ **over the 11 observed months** — computed at the aggregate level, not combined from SKU-level deviations, see §5 | same source as $\bar d_k$ |
| $\Gamma$ | Uncertainty budget (0 ≤ Γ ≤ \|K\|) — number of clusters allowed to simultaneously realize worst-case demand | **TBD** — sensitivity analysis parameter, no fixed value yet |
| $D_{\max}$ | Coverage threshold (km) for f2 | **TBD** — candidate: Paragon SLA, Java ≤150km / outer Java ≤500km |
| $\text{EF}^{\text{FM}}, \text{EF}^{\text{MM}}, \text{EF}^{\text{LM-Ind}}$ | Transport emission factors: First Mile / Direct = 79, Mid Mile = 360.83, Indirect Last Mile = 756 (gCO2e/tonne-km) | GLEC Framework, via `Emission_Factors` |
| $\text{EF}^{\text{MH}}, \text{EF}^{\text{SH}}$ | Warehouse emission factors: Mainly Handling = 1.3, Storage+Handling = 5.6 (kgCO2e/tonne) | GLEC Framework |
| $\text{KGPerPallet}_p$ | SKU-specific pallet-conversion factor, used once during preprocessing to convert raw KG/PCS demand to pallet-equivalent volume — see §4 | `ProductMaster` (5,174 SKUs, 0% missing); not carried into the optimization model as a product-indexed parameter |
| $\text{TonnesPerPallet}_k$ | Cluster-specific weighted-average pallet weight, $= \dfrac{\text{total KG historically ordered by cluster } k}{\text{total pallet-equivalent historically ordered by cluster } k}$ (ratio of totals, i.e. volume-weighted, not a simple average of per-SKU factors). Used only in $f_3$ to convert $\text{Delivery}_{j,k}$ (pallets) into tonnes for the GLEC emission factors — see §6 Open Items | Derived from `b2b_so` × `ProductMaster`, same source as $\bar d_k$ |
| $\overline{\text{TonnesPerPallet}}$ | Network-wide weighted-average pallet weight (same ratio-of-totals formula as $\text{TonnesPerPallet}_k$, but summed across all clusters in scope). Used only in $f_3$ to convert $\text{Transfer}_{j,l}$ (pallets) into tonnes, since a backbone Transfer arc mixes flow ultimately destined for many different clusters and cannot be attributed to one cluster's product mix | Derived from `b2b_so` × `ProductMaster`, network-wide aggregate |

---

## 4. Product Aggregation Assumption

Although the underlying transactional dataset contains **5,174 distinct SKUs** (`ProductMaster`), the optimization model does not index flow, demand, or cost by product. Products are heterogeneous at the transactional level — they differ in weight, packaging, and pallet density — but they are homogeneous with respect to the attributes that determine the strategic distribution-network-design problem addressed here. This is **not** an assumption that SKUs are interchangeable; it is an empirically verified structural property of this dataset within the modeled scope (Supply → Transfer → Last-Mile B2B).

**Construction.** For each SKU $p$, the observed order quantity is converted to pallet-equivalent volume using its own SKU-specific conversion factor ($\text{KGPerPallet}_p$, from `ProductMaster`):
$$
q_{k,p}^{\text{pallet}} = \frac{q_{k,p}^{\text{KG}}}{\text{KGPerPallet}_p}
$$
Pallet-equivalent volumes are then summed across all products for each demand cluster $k$ to obtain the aggregate pallet demand used throughout the model:
$$
\bar d_k = \sum_{p \in P} q_{k,p}^{\text{pallet}}
$$
No product-level detail is discarded prior to this step — the sum is over exact, SKU-specific pallet quantities, not an approximation from a single blended conversion factor.

**Empirical justification (verified against real data, not assumed):**

1. *Cost homogeneity.* `ENO_CostTransfer` and `ENO_CostLastMileB2B` — the two rate tables with route-level cost variation — contain no product-specific field; rates are defined at the (Origin, Destination) level only. `ENO_CostSupply` is uniformly 0 across all four factory origins (J1/J2/J4/J6 → NDC) and is therefore not informative for this check, but also cannot be affected by aggregation since it contributes nothing to $f_1$ regardless of product mix.
2. *Capacity additivity.* `FacilityMaster.CapacityInPallet` is a single scalar per facility with no per-product breakdown — every pallet consumes capacity identically regardless of contents.
3. *No downstream product-specific network eligibility.* `ENO_ProductionMapping` (Factory × Production Line × ProductGroup) constrains only which factory/line may produce a given product group; it does not reference any NDC/RDC/DC/Depot node. The candidate and backbone facilities modeled in $J$ are entirely downstream of this constraint and are therefore unaffected by product identity.
4. *Conservation.* 100% of `b2b_so` order lines, and 100% of ordered KG, match a `ProductID` in `ProductMaster` — the pallet-equivalent conversion loses no volume.
5. *Demand concentration (descriptive only).* Of 3,692 SKUs with observed B2B demand, the Herfindahl–Hirschman Index of pallet-equivalent volume is 0.0745 (top-10 SKUs = 46.4%, top-100 = 75.3%) — a moderately long-tailed distribution typical of FMCG. This statistic is reported for completeness only; it is **not** used as justification for aggregation. Aggregation validity here rests on points 1–3 (parameter homogeneity and absence of product-specific constraints), not on how concentrated or dispersed demand happens to be across SKUs.

**Rationale.** Because product identity does not appear in any cost coefficient, capacity constraint, or network-eligibility rule within the modeled scope, retaining a product index $p$ in the flow decision variables (e.g., a hypothetical $\text{Transfer}_{j,l,p}$) would add no decision-relevant information: the objective and constraints collapse algebraically back to their aggregate form once summed over $p$. This is treated as an **index-elimination simplification**, not an approximate one (cf. Melo, Nickel, & Saldanha-da-Gama, 2009, on facility-location model structure). It follows established practice in strategic supply-chain network design, where products sharing relevant logistics characteristics (source, cost structure, capacity consumption) are commonly grouped for facility-location-level modeling even when the underlying transactional catalog is large (Ballou, 2001; Simchi-Levi, Kaminsky, & Simchi-Levi, *Designing and Managing the Supply Chain*; Schniederjans, LeGrand, Hill, Watson, Lewis, Cacioppi, & Jayaraman, 2013, Ch. 13, "Data Aggregation in Network Design"). Multi-commodity formulations remain the appropriate choice when product-specific costs, capacities, network eligibility, or service requirements are present (e.g., Canel, Khumawala, Law, & Loh, 2001; Melo, Nickel, & Saldanha-da-Gama, 2006) — none of which hold in this dataset within the modeled scope.

---

## 5. Robust Demand Aggregation

Product aggregation (§4) and demand-uncertainty aggregation are distinct modeling decisions and are treated separately here.

The Bertsimas–Sim robust framework (§9) requires a nominal demand $\bar d_k$ and a deviation $\hat d_k$ for each cluster $k$. Both are defined **directly on the aggregate pallet-equivalent series**, not derived by first computing SKU-level uncertainty parameters and then combining them:

$$
\bar d_k = \text{sum of the aggregate monthly pallet-equivalent demand series at } k \text{ over the observed period (Jan–Nov 2025) — used directly, no annualization or extrapolation}
$$
$$
\hat d_k = \text{standard deviation of that same aggregate series across the 11 observed months}
$$

This ordering matters: $\bar d_k$/$\hat d_k$ are computed *after* summing pallet-equivalent volume across all SKUs for cluster $k$, not by first computing a per-SKU $\hat d_{k,p}$ and combining across products. The two are not generally equivalent — summing independent SKU-level uncertainty sets does not, in general, reduce to a single equivalent aggregate uncertainty set unless the SKU-level deviations satisfy specific structural conditions (e.g., identical budgets and comonotonic deviations).

**Choice of deviation measure: standard deviation, not max-minus-mean (RESOLVED 2026-09-13).** Two candidate formulas for $\hat d_k$ were compared empirically against the real 11-month series across all 1,763 active clusters: standard deviation, and (max month − mean). The max-minus-mean measure proved highly sensitive to a single unusual month — with only 11 observations per cluster, its ratio to $\bar d_k$ ranged up to 0.91 (one cluster's single peak month was nearly double its own average), against a maximum of 0.30 for the standard-deviation ratio, and a median of 0.06 vs. 0.03. A single anomalous month (e.g., a bulk or catch-up order) therefore dominates the max-minus-mean measure for several clusters, overstating their "typical" demand risk and disproportionately inflating the robust-protection term $\Gamma z + \sum_k p_k$ for those clusters based on a one-off event rather than genuine recurring variability. Standard deviation reflects dispersion across the full observed series and is markedly less sensitive to any single month, so it was adopted as $\hat d_k$.

This choice is deliberate and consistent with the network-design scope of the model: the robust protection term $\Gamma z + \sum_k p_k$ in $f_1$ (§9) protects against uncertainty in the **total pallet throughput** that a facility or arc must be capacitated/costed for — exactly the quantity $\bar d_k$/$\hat d_k$ represent when computed at the aggregate level. The model makes no claim about, and is not designed to protect against, SKU-level demand uncertainty (e.g., a scenario where SKU A rises 30% while SKU B falls 30%, leaving aggregate pallet volume unchanged, falls outside what this robust formulation addresses — and is not a relevant risk for the facility-location/flow-allocation decisions being optimized, since those decisions respond only to aggregate throughput per §4).

**Time-horizon decision: 11-month observed period, no extrapolation, no annualization.** The model is built directly on the full extent of available transactional data — January–November 2025 (11 months) — rather than extrapolating a fabricated 12th month or annualizing to a calendar-year total. Two considerations drove this:

1. *No structural requirement for annualization.* No supply-chain-network-design literature reviewed mandates that model inputs be scaled to a full calendar year — annualizing is a reporting convention for cross-study comparison, not a requirement of the optimization model itself. What the model requires (Park, *Fundamentals of Engineering Economics*, Ch. 6, "consistent time-basis" principle) is only that every parameter fed into it share the same time basis — which 11 real months uniformly satisfies.
2. *Extrapolation would introduce an unverified assumption, not remove one.* The company's own internal methodology for estimating a missing month (Dec2025 = Nov2025 × (1 + Nov→Dec year-over-year growth rate), computed at fine channel/area/category granularity) depends on 2024 data that is outside the scope of this thesis's dataset. Approximating that with a cruder proxy (e.g., scaling the 11-month average up by 12/11) would fabricate a month's demand without empirical support, adding noise to $\bar d_k$ rather than reducing it. Building network-design/robust-optimization models directly on an observed partial-year dataset, without fabricating the remainder, has precedent in comparable distribution-network-optimization studies (e.g., a 9-month real dataset).

Consequently: **no annualized or annual-equivalent figure is computed, reported, or used at any stage of this thesis** — not as a model input, and not as a post-optimization reporting convention. All demand, cost, flow, and emissions results are interpreted strictly on the observed 11-month (Jan–Nov 2025) basis throughout §7–§11. Extrapolating to a full year remains a possible future sensitivity check but is out of scope for the main model.

---

## 6. Decision Variables

| Variable | Domain | Description |
|---|---|---|
| $Y_j$ | $\{0,1\}$, $j \in J^{C}$ | 1 if candidate facility $j$ is open. $Y_j = 1$ fixed $\forall j \in J^{B}$ (not a free variable). |
| $\text{Transfer}_{j,l}$ | $\ge 0$, $(j,l) \in A^{T}$ | Flow (**pallet-equivalent**, per §4) from facility $j$ to facility $l$. Converted to tonnes only inside $f_3$ via $\overline{\text{TonnesPerPallet}}$ — see §7. |
| $\text{Delivery}_{j,k}$ | $\ge 0$, $(j,k) \in A^{D}$ | Flow (**pallet-equivalent**, per §4) from facility $j$ to demand cluster $k$. Converted to tonnes only inside $f_3$ via $\text{TonnesPerPallet}_k$ — see §7. |
| $\text{ExcessInv}_j$ | $\ge 0$, $j \in J$ | Inventory above usable capacity at $j$ (soft slack) |
| $z,\ p_k$ | $\ge 0$, $k \in K$ | Bertsimas–Sim linearization (dual) variables for the robust demand-protection term in $f_1$ |
| $\text{Cover}_k$ | $\{0,1\}$ (or relaxed $[0,1]$), $k \in K$ | 1 if cluster $k$ is covered by at least one open facility within $D_{\max}$ |

---

## 7. Objective Functions

### $f_1$ — Total Cost (minimize)

$$
f_1 = \sum_{(j,l)\in A^{T}} \text{TransferRate}_{j,l}\cdot\text{Transfer}_{j,l}
+ \sum_{(j,k)\in A^{D}} \text{B2BRate}_{j,k}\cdot\text{Delivery}_{j,k}
+ \sum_{j\in J} \text{FixedStorageCost}_j\cdot Y_j
$$
$$
+ \sum_{j\in J} \text{HandlingCostB2B}_j\cdot\Big(\sum_l \text{Transfer}_{j,l} + \sum_k \text{Delivery}_{j,k}\Big)
+ \sum_{j\in J} \text{StoragePenaltyPerPallet}_j\cdot\text{ExcessInv}_j
+ \Gamma z + \sum_{k\in K} p_k
$$

Notes:
- $Y_j := 1$ for $j \in J^{B}$ (not summed as a free cost driver for the fixed backbone, included for notational completeness — $F_j \cdot Y_j$ collapses to a constant for backbone nodes).
- Supply (Factory→NDC) term omitted — cost = 0 (§2.1/§5.5, Decision Log).
- IOC excluded (per Decision Log §4). B2C cost terms excluded (channel dropped).
- $\Gamma z + \sum_k p_k$ is the Bertsimas–Sim robust-cost protection term (see §9) guarding $f_1$ against worst-case demand surges at up to $\Gamma$ clusters simultaneously.

### $f_2$ — Uncovered Demand (minimize), MCLP-style

$$
f_2 = \sum_{k \in K} \bar d_k \cdot (1 - \text{Cover}_k)
$$

subject to (linearization):
$$
\text{Cover}_k \le \sum_{j \,:\, \text{Dist}_{j,k} \le D_{\max}} Y_j \qquad \forall k \in K
$$

(where $Y_j := 1$ for $j \in J^{B}$, so a cluster within range of any always-open backbone facility is automatically covered).

### $f_3$ — CO2 Emissions (minimize)

$$
f_3 = \underbrace{\sum_{(j,l)\in A^{T}} \text{EF}^{\text{MM}}\cdot\text{Dist}_{j,l}\cdot\big(\text{Transfer}_{j,l}\cdot\overline{\text{TonnesPerPallet}}\big)}_{\text{Transfer (Mid Mile)}}
+ \underbrace{\sum_{\substack{(j,k)\in A^{D}\\ j = \text{NDC}}} \text{EF}^{\text{FM}}\cdot\text{Dist}_{j,k}\cdot\big(\text{Delivery}_{j,k}\cdot\text{TonnesPerPallet}_k\big)}_{\text{LastMileB2B — Direct}}
+ \underbrace{\sum_{\substack{(j,k)\in A^{D}\\ j \ne \text{NDC}}} \text{EF}^{\text{LM-Ind}}\cdot\text{Dist}_{j,k}\cdot\big(\text{Delivery}_{j,k}\cdot\text{TonnesPerPallet}_k\big)}_{\text{LastMileB2B — Indirect}}
$$
$$
+ \underbrace{\sum_{j\in J^{C}} \text{EF}^{\text{MH}}\cdot\Big(\sum_l \text{Transfer}_{j,l}\cdot\overline{\text{TonnesPerPallet}} + \sum_k \text{Delivery}_{j,k}\cdot\text{TonnesPerPallet}_k\Big)}_{\text{Warehousing — Mainly Handling}}
+ \underbrace{\sum_{j\in J^{B}} \text{EF}^{\text{SH}}\cdot\Big(\sum_l \text{Transfer}_{j,l}\cdot\overline{\text{TonnesPerPallet}} + \sum_k \text{Delivery}_{j,k}\cdot\text{TonnesPerPallet}_k\Big)}_{\text{Warehousing — Storage+Handling}}
$$

$\text{Transfer}_{j,l}$/$\text{Delivery}_{j,k}$ are pallet-equivalent (§4/§6); the $(\cdot\ \text{TonnesPerPallet})$ factors convert to tonnes only for this objective — cluster-specific $\text{TonnesPerPallet}_k$ for Delivery arcs (single identifiable destination cluster), network-wide $\overline{\text{TonnesPerPallet}}$ for Transfer arcs (backbone flow mixes many clusters' product mix, so no single cluster ratio applies). Distance = `DistanceInKM` (real OSRM/sea-routing). Excludes Production, Automation, B2C/Instant Delivery (out of scope).

---

## 8. Constraints

**(1) Flow balance at every facility, per node:**
$$
\sum_{l\,:\,(l,j)\in A^{T}} \text{Transfer}_{l,j} \;+\; \mathbb{1}[j=\text{NDC}]\cdot(\text{Supply from Factory, cost}=0)
\;=\; \sum_{l\,:\,(j,l)\in A^{T}} \text{Transfer}_{j,l} \;+\; \sum_{k\,:\,(j,k)\in A^{D}} \text{Delivery}_{j,k}
\qquad \forall j \in J
$$

**(2) Robust demand satisfaction** (worst-case realization within the uncertainty set — see §7 for the linearized robust counterpart):
$$
\sum_{j\,:\,(j,k)\in A^{D}} \text{Delivery}_{j,k} \;\ge\; \bar d_k \qquad \forall k \in K
$$
(nominal feasibility always required; §9 adds the cost-side protection against $d_k$ exceeding $\bar d_k$ by up to $\hat d_k$ for at most $\Gamma$ clusters simultaneously.)

**(3) Facility capacity (inventory):**
$$
\text{TotalInv}_j = \Big(\sum_l \text{Transfer}_{j,l} + \sum_k \text{Delivery}_{j,k}\Big)\cdot \frac{\text{DOS}_j}{360}
$$
$$
\text{ExcessInv}_j \ge \text{TotalInv}_j - \text{Cap}_j, \qquad \text{ExcessInv}_j \ge 0 \qquad \forall j \in J
$$

**(4) Linking — flow only through open facilities:**
$$
\sum_l \text{Transfer}_{j,l} + \sum_k \text{Delivery}_{j,k} \;\le\; M \cdot Y_j \qquad \forall j \in J^{C}
$$
(no flow may originate from a closed candidate facility; $M$ = a valid big-M, e.g. total network demand).

**(5) No self-transfer:**
$$
\text{Transfer}_{j,j} = 0 \qquad \forall j \in J
$$

**(6) Fixed backbone forced open:**
$$
Y_j = 1 \qquad \forall j \in J^{B}
$$

**(7) Coverage linearization:** see §7, $f_2$.

**(8) Domain constraints:**
$$
Y_j \in \{0,1\}\ \forall j\in J^{C}, \quad \text{Cover}_k \in \{0,1\}\ \forall k \in K, \quad \text{Transfer}_{j,l},\ \text{Delivery}_{j,k},\ \text{ExcessInv}_j,\ z,\ p_k \ge 0
$$

---

## 9. Robust Counterpart (Bertsimas & Sim, 2004 — Budget of Uncertainty)

Demand at cluster $k$ is uncertain: $d_k \in [\bar d_k - \hat d_k,\ \bar d_k + \hat d_k]$, with no assumed probability distribution. The uncertainty budget $\Gamma \in [0, \lvert K \rvert]$ bounds how many clusters may simultaneously realize their worst-case (maximum) demand — protecting against joint worst-case cost exposure without the full conservatism of assuming every cluster deviates at once ($\Gamma = \lvert K \rvert$) nor ignoring uncertainty entirely ($\Gamma = 0$).

Following Bertsimas & Sim's linearized dual reformulation, the robust cost-protection term added to $f_1$,
$$
\Gamma z + \sum_{k \in K} p_k,
$$
is enforced by:
$$
z + p_k \;\ge\; \hat d_k \cdot \lambda_k \qquad \forall k \in K
$$
$$
z \ge 0, \qquad p_k \ge 0 \qquad \forall k \in K
$$

where $\lambda_k$ is the marginal cost of serving one additional unit of demand at cluster $k$ (e.g., $\lambda_k = \min_{j\,:\,(j,k)\in A^{D}} \text{B2BRate}_{j,k}$). This guarantees $f_1$ remains a valid upper bound on cost for every demand realization in which at most $\Gamma$ clusters deviate to $\bar d_k + \hat d_k$ simultaneously, at the price of no additional binary/integer variables (the robust counterpart stays linear).

**Interpretation of $\Gamma$:** $\Gamma = 0$ recovers the deterministic (nominal-demand) model; $\Gamma = \lvert K \rvert$ recovers the fully conservative model (every cluster protected at its maximum simultaneously). The "price of robustness" — degradation in $f_1$ as $\Gamma$ increases — is explored via sensitivity analysis (Open Item: starting range for $\Gamma$ not yet chosen).

---

## 10. Solution Methodology

**Stage 1 — Mathematical modeling.** Formulate the Robust MOMILP above (3 objectives $f_1, f_2, f_3$; Bertsimas–Sim robust cost-protection term; binary $Y_j$, $\text{Cover}_k$). Implemented in **Pyomo**.

**Stage 2 — Pareto optimization.** **AUGMECON2** (Mavrotas & Florios, 2013) — augmented ε-constraint method — generates the exact non-dominated Pareto frontier over $(f_1, f_2, f_3)$: payoff table construction, ε-grid over the two constrained objectives, bypass-coefficient acceleration. Solved with **HiGHS**.

**Stage 3 — Managerial evaluation.** **TOPSIS** ranks the Pareto-optimal network configurations under each weighting scenario $w \in W$ (Cost-Driven, Service-Driven, Balanced/Green), using **pymcdm**.

**Toolchain:** Python — Pyomo + pyaugmecon + HiGHS + pymcdm.

---

## 11. Expected Outputs

1. **Pareto frontier** — the full set of non-dominated $(f_1, f_2, f_3)$ solutions from AUGMECON2 (table + 3D/parallel-coordinates visualization).
2. **Facility configuration per Pareto solution** — which of the 20 candidate "Last-Mile Facility" nodes ($Y_j$) are open, for each point on the frontier.
3. **Flow allocation per Pareto solution** — Transfer and Delivery volumes across the network.
4. **TOPSIS ranking table** — Pareto solutions ranked under each of the 3 weighting scenarios, with the recommended configuration per scenario.
5. **Sensitivity analysis over $\Gamma$** — how the Pareto frontier / recommended network shifts as the uncertainty budget increases (price of robustness).
6. **Sensitivity analysis over $D_{\max}$** (once resolved) — impact of the coverage threshold choice on $f_2$ and the resulting network.
7. **Managerial trade-off narrative** — cost vs. service-level vs. emissions trade-offs, framed for the thesis's recommendation chapter.

---

## Open Items Affecting This Formulation

- **$\hat d_k$ formula (RESOLVED 2026-09-13):** standard deviation of the 11-month aggregate pallet series, not max-minus-mean — see §5 for the empirical comparison across 1,763 active clusters that drove this choice.
- $\Gamma$ (uncertainty budget) — starting range not yet chosen.
- $D_{\max}$ (coverage threshold) — candidate values identified (Paragon SLA), not yet confirmed.
- Geography scope — **CONFIRMED: Java-only** (2026-09-13). Ocean-transport terms in $f_3$ are now dropped entirely (single-mode truck network). Recount of $\lvert J \rvert$, $\lvert J^{B} \rvert$, $\lvert J^{C} \rvert$, $\lvert K \rvert$ for Java-only still pending — needs to be re-run against real data.
- Missing-lane cost/distance estimation (for $(j,l) \notin$ observed `ENO_CostTransfer`/`ENO_CostLastMileB2B` but $(j,l) \in A^{T}/A^{D}$ by topology) — methodology decided (§5.5/§5.7, Decision Log), not yet implemented.
- **Unit consistency (RESOLVED 2026-09-13):** $\text{Transfer}_{j,l}$/$\text{Delivery}_{j,k}$ are now defined in pallet-equivalent units throughout (§6), matching the pallet-based cost rates and capacity (§3). $f_3$ (§7) converts to tonnes only where needed, using $\text{TonnesPerPallet}_k$ (cluster-specific, weighted average) for Delivery arcs and $\overline{\text{TonnesPerPallet}}$ (network-wide weighted average) for Transfer arcs. Still pending: compute the actual $\text{TonnesPerPallet}_k$/$\overline{\text{TonnesPerPallet}}$ values from `b2b_so` × `ProductMaster` (§3.2 in `Model.ipynb`).
- **Time horizon (RESOLVED 2026-09-13):** Model is built directly on the observed 11-month period (Jan–Nov 2025) — see §2, §5. No extrapolation of December 2025, and no annualized/annual-equivalent figure at any stage (model input or reporting). Extrapolation (previously "Option A") is out of scope, not even as a sensitivity check, per explicit decision. **Still pending:** confirm the native granularity of $\text{FixedStorageCost}_j$ in `FacilityMaster` (is it a full contractual annual figure, or already period-actual for the data window?) — this determines whether it needs any period adjustment to combine consistently with the 11-month flow-based cost terms in $f_1$; not yet resolved.

*See `Decision_Log.md` for full reasoning behind every scope and data decision referenced above.*

---

## References

- Ballou, R. H. (2001). Unresolved issues in supply chain network design. *Information Systems Frontiers*, 3(4), 417–426. https://doi.org/10.1023/A:1012872704057
- Bertsimas, D., & Sim, M. (2004). The price of robustness. *Operations Research*, 52(1), 35–53. https://doi.org/10.1287/opre.1030.0065
- Canel, C., Khumawala, B. M., Law, J., & Loh, A. (2001). An algorithm for the capacitated, multi-commodity multi-period facility location problem. *Computers & Operations Research*, 28(5), 411–427. https://doi.org/10.1016/S0305-0548(99)00126-4
- Mavrotas, G., & Florios, K. (2013). An improved version of the augmented ε-constraint method (AUGMECON2) for finding the exact Pareto set in multi-objective integer programming problems. *Applied Mathematics and Computation*, 219(18), 9652–9669.
- Melo, M. T., Nickel, S., & Saldanha-da-Gama, F. (2006). Dynamic multi-commodity capacitated facility location: A mathematical modeling framework for strategic supply chain planning. *Computers & Operations Research*, 33(1), 181–208. https://doi.org/10.1016/j.cor.2004.07.005
- Melo, M. T., Nickel, S., & Saldanha-da-Gama, F. (2009). Facility location and supply chain management — A review. *European Journal of Operational Research*, 196(2), 401–412. https://doi.org/10.1016/j.ejor.2008.05.007
- Schniederjans, M. J., LeGrand, S. B., Hill, A. V., Watson, M., Lewis, S., Cacioppi, P., & Jayaraman, J. (2013). *Supply chain design: Applying optimization and analytics to the global supply chain*, Ch. 13 "Data Aggregation in Network Design". FT Press.
- Simchi-Levi, D., Kaminsky, P., & Simchi-Levi, E. *Designing and managing the supply chain* (3rd ed.). McGraw-Hill.

*Note: full bibliographic detail (volume/issue/pages) for the Simchi-Levi et al. textbook should be confirmed against the exact edition available to you before submission.*
