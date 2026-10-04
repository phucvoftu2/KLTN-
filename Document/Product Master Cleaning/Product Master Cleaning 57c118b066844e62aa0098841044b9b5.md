# Product Master Cleaning

Client / EngagementParagon - ENO: Paragon - ENO
ETA: July 16, 2026
Initiative type: Data Cleaning
Lead author: Ngoc Nguyen
Meeting: None
Reviewer: Duy Tran
Status: Final

# Part 1 - Fixed Template

## Summary

This initiative turned the raw product list into a clean "Product Master" - one trustworthy record per product with weight, packaging, pallet, factory, and category details filled in wherever possible. This Product Master is the reference table that every other analysis (inventory, demand grouping, SO, STO, Model running) joins against.

- **What was the initiative?** A data-cleaning pipeline in R that standardises raw product data, fills in missing weight/pallet/category values using several fallback methods, assigns each product to a filling-machine type (PTG) and a factory, and produces one final reference table.
- **Why the client needed it:** The raw product data has inconsistent formatting and many missing values (weight, pallet quantity, PTG, factory). Every downstream model needs these fields populated and consistent - without this cleaning step, models would be working with incomplete product data.
- **What it produced (deliverable + link):**
    - `DATA/02.Cleaned_data/ProductMaster.parquet` - the final, clean Product Master used by all downstream analyses.
    - `DATA/03.Summarized_data/Product_list_with_pallet_conversion_rate.xlsx` — list of products with a suspicious pallet quantity (exactly 1 piece per pallet) for client review.
- **Key results / recommendation:** Missing weight , pallet quantity, and PTG values were filled using a sequence of fallback rules (described in Method), so the great majority of products now have complete data. A short list of products still has a suspicious pallet conversion rate (1 piece/pallet).

Most of the data is filled and has no impact in the model. The reason for this is the number of SKUs the appeared in the SO is filled (We only use SKUs that appeared in the SO for the model) so the SKUs that stay outside the SO records is not having any impact.

| Missing Value | Missing percentage before | Missing percentage after  |
| --- | --- | --- |
| PTG  | 34.17% ~ 1768 SKUs | 3.29% ~ 171 SKUs |
| GrossWeightInGram | 6.76% ~ 350 SKUs | 0% |
| NetWeightInGram | 8.11% ~ 420 SKUs | 0% |
| QuantityPiecesPerPallet | 0.12% ~ 6 SKUs | 0% |
- [x]  A reader with no context understands purpose and outcome from this section alone

---

## Method

**Approach:**

The pipeline cleans the data and fills in gaps in five broad steps:

1. **Standardise.** Rename columns to clear, consistent names; standardise text casing; remove exact duplicate rows.
2. **Fill in category and packaging gaps.**
3. **Assign PTG (filling-machine type).** 
4. **Fill in weight and pallet quantity.** 
5. **Finalise.** 

Detailed pipeline will be placed in Part 2.

**Why this approach (alternatives rejected):** A simple "drop missing rows" approach was rejected because too many real products would be lost. Filling gaps from related products (sharing a barcode, category, or PTG) was preferred over inventing default values, because it reuses real information that already exists elsewhere in the data rather than guessing.

**Scope - what it covers and what it does not:**

- Covers: all products in the raw client extract; a small set of known status overrides (4 specific product codes are kept active even though flagged inactive in the source).
- Excludes: products that have no barcode, no related product, and no client conversion-rate record - these remain with missing fields and are not invented.

**Units & conventions:** Weight in grams (converted to KG-per-pallet for one derived field). Pallet and koli quantities in pieces. 

- [x]  Approach and scope are clear to someone who knows the technique

---

## Pitfalls & Reuse

**What would have saved you a full day if you'd known it on day one?**
Run `QuickExploreData()` after each pass (as the script does) to see how many NAs remain at each step.

**What's the one step that breaks if done out of order?**

Step 4 (weight and pallet-quantity gap-filling) must run after Step 3 (PTG
assignment) completes, not because PTG affects the weighted average calculation
itself, but because both steps read from and write to the same object
(`ProductMaster_PTG_complete`), which Step 3 is still building. Running Step 4
mid-way through Step 3 means the object it reads from is incomplete, in particular,
`ProductBarcode` (needed for the barcode-level grouping in the weight fill) may not
yet have been joined in. The join would silently return blank barcodes, and the
weighted average would group incorrectly or not at all.

**What did you do by hand that isn't in any script?**

- Four specific product codes (`00028`, `00002`, `00001`, `05084`) are hardcoded to stay "active" even if the raw data marks them inactive. This was a manual exception.
- The three subcategories forced to PTG "OEM" (Make Up Tools, Bags & Accessories, Clothing) are a manual business rule, not derived from data.
- The factory code recoding (e.g. `JTK02` → `J2`) is a hardcoded lookup for four factory IDs.

**What here is directly reusable, and where is it?**

| Asset | Location | Reusable for |
| --- | --- | --- |
| Cascading fallback-fill pattern (barcode → category → sales-volume-weighted) | PTG and weight-filling steps | Any field that needs gap-filling from related records, in any dataset |
| `FormatColumnName()`, `QuickExploreData()` | Setup / used throughout | Standard column cleanup and data-quality snapshot for any new raw extract |
- [x]  All six questions answered; reviewer challenged any that look evasive

---

## Inputs

**Script location:** `ANALYSIS/PRGN.Clean_ProductMaster.Rmd`

**Main data sources:**

- Raw product master extract from the client (`Raw_ProductMaster_20251219.parquet`)
- An older extract used only for product segment/description (`Raw_ProductMaster_20251112.RData`)
- SKU-to-PTG mapping (`SKU_PTG.parquet`) - also the source of factory assignments
- 2025 full-year sales history - used to weight-average missing weights and to break ties when multiple PTGs are possible for a barcode
- A client-provided weight/pallet conversion-rate file, used as a last-resort fallback
- The product grouping output (from the separate Product Grouping initiative), joined in to attach `ProductGroupID`
- MFC-eligible product list, used to flag MFC products

Check **Data input table** for data path

**External references:** None.

- [x]  Main sources named and traceable; detail deferred to Part 2

---

## Outputs & Where It Landed

**Final deliverables:**

- `ProductMaster.parquet` - the single source of truth for product attributes (weight, pallet size, category, PTG, factory, MFC flag) used by every downstream initiative.
- `Product_list_with_pallet_conversion_rate.xlsx` - products with a pallet quantity of exactly 1, for client confirmation.

**Where it landed:** `ProductMaster.parquet` is read by virtually every other pipeline in this project (inventory cleaning, product grouping, flow balancing, MFC allocation, network planning).

- [x]  Outputs located and their interpretation explained

---

## Runtime Expectations

- **Run Time:** 5 mins.
- **Hardware / environment measured on:** R Studio.
- [x]  If the initiative runs, a runtime estimate tied to input complexity is given

---

# Part 2 - Detailed Body

**Source-of-truth line:** This document is the authoritative reference for the pipeline that produces `ProductMaster.parquet`, the canonical product reference table for the project.

---

The pipeline cleans the data and fills in gaps in five broad steps:

1. **Standardise.** Rename columns to clear, consistent names; convert blank/`"NULL"` text and zero values to proper missing values (NA) so they can be detected and handled; standardise text casing; remove exact duplicate rows.
2. **Fill in category and packaging gaps.** Where `Segment` or `ContainerType` is missing for a product, look up the value from another product that shares the same category or barcode and already has it filled in.
3. **Assign PTG (filling-machine type).** This is the most involved step. Many products don't have a PTG recorded directly, so the pipeline fills the gap using a cascade of fallback rules, each one only used if the previous one didn't find an answer:
    - Use the product's own PTG if known.
    - Otherwise, use the PTG of another product with the same barcode and container type, if there's only one possible answer.
    - Otherwise, use the PTG shared by other products with the same subcategory, product format, description, and container type.
    - Otherwise, relax the match further (subcategory, product format, container type only).
    - Otherwise, use the PTG of whichever product on the same barcode accounts for the largest share of sales volume.
    - A few subcategories (Make Up Tools, Bags & Accessories, Clothing) are always set to PTG "OEM" directly, since these aren't filled on a production line.
4. **Fill in weight and pallet quantity.** Where a product's gross weight, net weight, or pallet quantity is missing, the pipeline fills it in using (in order): a sales-volume-weighted average from other records of the same barcode, then a separate client-provided conversion-rate file, if still missing.
5. **Finalise.** Join in the product group, recode a few internal factory codes to standard names, relabel the "Watsons" brand as "Manufacturer", and assign each product to a factory (using the product's own factory if known, otherwise the factory typically associated with its PTG). Flag MFC-eligible products. Write the final table.

## Worked Example - One Product's Journey

To make the fallback cascade concrete: imagine `ProductID = "04412"`, barcode `8993137712743`, with no `PTG`, no `GrossWeightInGram`, and no `QuantityPiecesPerPallet` in the raw extract.

1. **Standardise (Step 1):** Its blank text fields are converted from `"NULL"`/`""` to proper NA. Its `Status` field, formatting, and casing are normalised.
2. **PTG fallback (Step 3):**

The product's own `PTG` is NA — first pass finds nothing.

The pipeline checks other `ProductID`s sharing barcode `8993137712743` and the same `ContainerType`. Suppose two other records share that barcode and container type, and both already have `PTG = "Liquid Filling"`. Since there's exactly one distinct PTG among them, this product is filled with `"Liquid Filling"` at this pass.

1. **Weight/pallet fallback (Step 4):** Other `ProductID`s sharing barcode `8993137712743` have varying recorded weights. The pipeline computes a sales-volume-weighted average gross weight across all of them (using 2025 sales quantities as weights) and fills this product's `GrossWeightInGram` with that average. The same logic fills `QuantityPiecesPerPallet`.
2. **Result:** The final `ProductMaster.parquet` row for `ProductID = "04412"` now has a complete `PTG`, `GrossWeightInGram`, and `QuantityPiecesPerPallet` — none of them directly observed for this specific `ProductID`, all of them borrowed from sibling records on the same barcode.
- *(This is an illustrative walk-through to explain the mechanism, not an audited example from the live data)*

## How Gaps Get Filled - Plain-Language Summary

| Override | What it does |
| --- | --- |
| 4 product codes (`00028`, `00002`, `00001`, `05084`) | Forced to stay **active** even if the raw data marks them inactive |
| 3 subcategories (Make Up Tools, Bags & Accessories, Clothing) | Forced to PTG **OEM** regardless of any other match |
| 4 factory codes (`JTK02`, `JTK01`, `JTK04`, `JTK06`) | Renamed to short internal codes (`J2`, `J1`, `J4`, `J6`) |

| Field | Fallback order (first match wins) |
| --- | --- |
| `Segment` | 1. Own value → 2. Another product in the same `Category` |
| `ContainerType` | 1. Own value → 2. Another product with the same barcode |
| `PTG` | 1. Own value → 2. Same barcode + container type → 3. Same subcategory/format/description/container → 4. Same subcategory/format/container (looser match) → 5. Most common PTG by sales volume for that barcode → 6. Forced "OEM" for 3 specific subcategories |
| `GrossWeightInGram` / `NetWeightInGram` / `QuantityPiecesPerPallet` | 1. Own value → 2. Sales-volume-weighted average from same barcode → 3. Client conversion-rate file |
| `FactoryID` / `FactoryType` | 1. Product's own factory → 2. Typical factory for that product's PTG |

---

## Output Schema (Key Fields)

| Field | Meaning |
| --- | --- |
| `ProductID`, `ProductBarcode` | Product identifiers |
| `ProductGroupID` | Link to the product grouping table |
| `GrossWeightInGram`, `NetWeightInGram` | Product weight |
| `QuantityPiecesPerPallet`, `KGPerPallet`, `QuantityPiecesPerKoli` | Packaging/handling units |
| `Brand`, `Category`, `SubCategory`, `Segment` | Commercial classification |
| `PTG`, `PTGCode` | Filling-machine type and its short code |
| `FactoryID`, `FactoryType` | Assigned production factory |
| `IsMFC` | Whether this product is eligible for Micro-Fulfillment Center allocation |

---

## Data Input Table

| Input | Path | Period | Known Issues |
| --- | --- | --- | --- |
| Raw product master extract | `DATA/01.Data_from_client/Master Data/Raw_ProductMaster_20251219.parquet` | Snapshot 2025-12-19 | Source of most fields |
| Older product master extract | `DATA/01.Data_from_client/Master Data/Raw_ProductMaster_20251112.RData` | Snapshot 2025-11-12 | Used only for Segment/Description - confirm this is still the best source, or if a newer file now carries these fields too (Open Item 2) |
| SKU-to-PTG mapping | `DATA/02.Cleaned_data/SKU_PTG.parquet` | Current | Also source of factory assignment |
| 2025 sales history | `DATA/05.Historical_baseline/SO_2025_FullYear_With_Value.parquet`; `DATA/03.Summarized_data/SO_Inventory_report_Jan_Nov.parquet` | Full year (one source labelled Jan–Nov — confirm these two sales files are consistent with each other) | Used for weighted averages and tie-breaking; if 2025 sales patterns are unusual, fallback values inherit that distortion |
| Conversion-rate file | `DATA/01.Data_from_client/Master Data/Raw_ProductMaster_conv_rate_20251219.parquet` | Snapshot 2025-12-19 | Last-resort fallback only |
| MFC-eligible product list | `DATA/02.Cleaned_data/MFC_Product_List.parquet` |  |  |
| Weight/pallet conversion-rate file | `DATA/01.Data_from_client/Master Data/Raw_ProductMaster_conv_rate_20251219.parquet` |  |  |
| Product grouping | `DATA/03.Summarized_data/Grouping/GroupingProducts_Adjusted.parquet` |  |  |

---

## Global Assumptions

| Assumption | Rationale |
| --- | --- |
| A barcode's most common PTG (by sales volume) is the correct PTG for products on that barcode with no other PTG signal | Best available proxy when no direct or category match exists |
| Make Up Tools, Bags & Accessories, and Clothing are always PTG "OEM" | Business rule — these are not made on a filling line |
| The 4 listed product codes should remain active even if marked inactive in the source | Manual exception, presumably confirmed with the client at the time — rationale not documented in code |
| Missing weight/pallet data can be safely estimated from other records of the same barcode | Assumes products sharing a barcode are physically identical or near-identical |

---

## Limitations

- Products with no barcode and no PTG/weight/pallet signal anywhere in the data remain incomplete; no value is invented for these.
- The weighted-average fallback for weight and pallet quantity depends on 2025 sales history - a product with little or no 2025 sales has a weaker fallback signal.
- The rationale for the 4 hardcoded "always active" product codes is not documented anywhere - only the codes themselves are visible in the script.

---

### Definition of Done (reviewer checks each)

- [x]  **Reproducibility path** — Another analyst can re-run the script top to bottom with updated raw files and regenerate `ProductMaster.parquet`.
- [x]  **Data inputs, fully traced** — Table above covers all 5 inputs.
- [x]  **Tools, code & files** — Single R Markdown script: `ANALYSIS/PRGN.Clean_ProductMaster.Rmd`. Key packages: `arrow`, `dplyr`, `stringr`, `CELRPackage` (`FormatColumnName`, `QuickExploreData`, `LoadRData`).
- [x]  **Global assumptions, each with a rationale** — Table above.
- [x]  **Limitations** — Section above.
- [x]  **Open items / things to validate** — 3 items listed above.
- [ ]  Open-items section present and honest
- [x]  Reproducibility path verified by reviewer

---

## Appendix

### Suspicious Pallet Quantity Check

The script flags any product with `QuantityPiecesPerPallet == 1` — a value that's almost always a data error rather than a real single-piece pallet. This list is exported for client review before the cleaned data is trusted for any pallet-based calculation (e.g. truck loading, warehouse space planning).

### Glossary

| Term | Meaning |
| --- | --- |
| **PTG** | Identifies which physical filling/packing line a product runs on. |
| **PTGCode** | A short, sequential code (e.g. `PTG01`, `PTG02`) assigned to each distinct PTG value, used as a compact identifier in other tables. |
| **Koli** | A secondary packing unit between a single piece and a pallet, used for inner-box-level handling. |
| **Barcode (`ProductBarcode`)** | A code that can be shared by multiple distinct `ProductID`s representing the same physical item under different internal codes. This pipeline borrows attributes (PTG, weight, pallet quantity) across `ProductID`s that share a barcode. |
| **Segment / Category / SubCategory** | Three-level commercial classification hierarchy, broadest to narrowest. |
| **KGPerPallet** | Derived field: total weight of a fully loaded pallet, in kilograms. |
| **IsMFC** | Flag indicating whether a product is eligible for allocation to a Micro-Fulfillment Center. |