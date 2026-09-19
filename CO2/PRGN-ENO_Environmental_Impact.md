# PRGN-ENO Environmental Impact

**Demand Supply Alignment**\
**PRGN-ENO**\
**Environmental Impact**\
**July 2026**

## Agenda

1.  Review other companies methodology
2.  Executive Summary
3.  Key Assumptions & Methodology
4.  Transportation
5.  Warehousing & Production
6.  Reflection
7.  Q&A

## 1. How Companies Estimate Their CO₂

### Common CO₂ Emission Sources Across the Supply Chain

Supply chain emission sources include:

-   Manufacturing
-   Raw Material
-   Transfer
-   Delivery
-   Electricity
-   Other energy
-   Outsourcing
-   Packaging
-   First & Mid Mile
-   Last Mile B2B & B2C

Emission scopes:

-   Scope 1: Direct emissions from owned operations.
-   Scope 2: Indirect emissions from purchased energy.
-   Scope 3: Indirect emissions from outsourced activities.

## Common Approaches to CO₂ Calculation

Companies can use different methods depending on the emission source,
data availability and policy:

1.  Direct measurement
    -   Metered or monitored emissions from controlled assets.
    -   Best for owned facilities and large factories.
2.  Activity data × Emission Factor
    -   Activity volume multiplied by an emission factor.
    -   Best for electricity, fuel, freight and standard reporting.
3.  Engineering Models
    -   Detailed operational modelling using load factor, vehicle,
        route, etc.
    -   Best for logistics and scenario analysis.
4.  Hybrid methods
    -   Combine primary data with secondary databases to fill gaps.
5.  Spend-based
    -   Estimate emissions from spend using cost intensity.
6.  Proxy / benchmark
    -   Use similar assets, suppliers or categories as proxy.

## Selected Company CO₂ Calculation Examples

### Toyota (Japan)

-   Electricity:
    -   CO₂ = Electricity consumption (kWh) × EF (kgCO₂e/kWh)
-   Other energy:
    -   CO₂ = Fuel consumption × Standard Calorific Value × EF
-   Raw materials and services:
    -   Based on purchase price.
-   Logistics:
    -   Fuel consumption × EF
    -   Volume × Distance × EF
-   Well-to-wheel:
    -   Number of cars sold × Vehicle emission × Lifetime mileage.

### Intel (USA)

-   Electricity:
    -   CO₂ = Electricity consumption × EF - Renewable electricity
-   Direct emissions:
    -   CO₂ = M (kg) × GWP
-   Purchased goods and services:
    -   Supplier-specific emissions + spend amount × emission factor.
-   Logistics:
    -   Distance travelled × EF × Volume.

### Unilever (UK)

-   Purchased goods and services:
    -   Purchased volume × Total emission factors.
-   User emissions:
    -   Total sales volume × Resource usage per use × EF.
-   Logistics:
    -   Distance travelled × EF + hotel nights × EF.

## Framework Contributions to Emission Calculations

  -----------------------------------------------------------------------
  Framework         Category          Parameter         Scope
                                      Provided          
  ----------------- ----------------- ----------------- -----------------
  IPCC, IEA         Energy & Product  Global warming    1, 2, 3
                    Use               potential, grid   
                                      emission factor   

  US EPA, MOE,      Operations &      Regional emission 1, 2
  DEFRA             Energy            factors,          
                                      calorific value   

  Ecoinvent, LCI,   Raw Materials     Cradle-to-gate    3
  IDEA                                emission factor   

  METI, MLIT, WLTP, Transport &       Distance/fuel     3
  GLEC              Product Use       emission factor   
  -----------------------------------------------------------------------

# 2. Paragon Project

## Executive Summary

### Situation

Paragon wants to understand not only cost impact, but also how CO₂
emissions increase or decrease under each proposed network change
compared with the baseline scenario.

### Questions

1.  What is the operational CO₂ footprint of the 2030 network?
2.  How will emissions change under each proposed network scenario?
3.  Which supply chain activities contribute most to total CO₂
    emissions?

### Answers

-   Current baseline generates **46,116 tCO₂**.
-   Future Network reduces total emissions to **43,065 tCO₂ (-6.6%)**.
-   Production is the largest contributor (\~65%).

### Impact

-   Approximately **3,051 tCO₂e avoided annually** under the Future
    Network.
-   Transportation redesign delivers the main actionable reduction
    opportunity.

## Approach Direction

A five-level framework guides the selection of data sources and emission
factors:

1.  Company
2.  Area
3.  Region
4.  Continent
5.  Global

Selected references:

-   BASF
-   Apple
-   DEFRA
-   EPA
-   ACE
-   JEC
-   EMEP/EEA
-   Ecoinvent
-   IEA

## End-to-End Supply Chain CO₂

Emission categories:

-   Production
    -   Manufacturing
-   Warehousing
    -   Storage + Handling
    -   Automation
-   Transportation
    -   First Mile (FTL)
    -   Mid Mile (LTL)
    -   Last Mile B2B & B2C

## Transportation Methodology

Formula:

**CO₂ = Volume × Distance × Emission Factor**

Assumptions:

-   Emission factors derived from GLEC reference data and
    country-specific datasets.
-   Shipment weight includes product weight and packaging materials.
-   Distance based on shortest feasible distance with 5% routing
    inefficiency adjustment.
-   Factors consider fleet utilization, load factor and empty return
    trips.

Transport categories:

  Category            Vehicle Type             EF Unit
  ------------------- ------------------------ -----------
  First Mile          Dry Van / TL Container   gCO₂/t-km
  Mid Mile            Blind Van / Truck        gCO₂/t-km
  Last Mile B2B/B2C   Van                      gCO₂/km
  Sea Transport       Container Ship           gCO₂/t-km
  Instant Delivery    Motorcycle               gCO₂/km

## Warehousing & Production Methodology

### Warehousing

Formula:

**CO₂ = Outbound (MT) × Emission Factor**

Categories:

-   Mainly Handling: 1,300 gCO₂/MT
-   Storage + Handling: 5,600 gCO₂/MT

### Production

Formula:

**CO₂ = Production Volume (MT) × Emission Factor**

Production proxies:

  Product Type     Emission Factor
  -------------- -----------------
  Liquid           274,000 gCO₂/MT
  Semi Solid       409,000 gCO₂/MT
  Powder           423,000 gCO₂/MT

## Automation Scenario

Automation reduces labor-dependent energy while increasing electricity
consumption from equipment.

Key assumptions:

-   Labor reduction proportionally reduces labor-related energy
    consumption.
-   Automation equipment uses rated average power consumption.
-   Electricity emissions use Indonesia grid emission factor (0.76
    kgCO₂e/kWh).
-   Embodied emissions from equipment manufacturing are excluded.

Result:

-   Total decrease: 128 tCO₂
-   Total increase from equipment energy: 2,066 tCO₂

# 3. New CO₂ Framework

## EcoTransIT Framework

EcoTransIT calculates emission factors using:

-   Vehicle type
-   Payload
-   Load factor
-   Empty running
-   Road type
-   Gradient
-   Fuel
-   Country

Formula:

**Emissions = Weight × Distance × EF**

Steps:

1.  Calculate load factor.
2.  Calculate empty running.
3.  Calculate vehicle energy consumption.
4.  Convert into tonne-km.
5.  Calculate fuel emission.
6.  Calculate emission factor per leg.

## Reflection

### What Went Well

-   Built a clear data hierarchy, prioritizing Paragon and
    Indonesia-specific data before broader benchmarks.
-   Converted network scenarios into comparable CO₂ impacts across
    transportation, warehousing and production.

### Areas for Improvement

-   Replace benchmark factors with actual fuel, electricity and
    production-energy data where available.
-   Validate key assumptions and emission-factor mappings with the
    client earlier.
