# Backlog — KLTN Thesis: Distribution Network Design (MOO-MCDM)

**Purpose:** Contingency items to revisit if the current scope proves too tight once modeling/data work goes deeper — checked periodically so scope issues get caught early instead of being patched around indefinitely.

---

## 1. Re-check scope fit: B2C inclusion / Sumatra expansion (added 2026-09-14)

**Why this is here:** the current scope (B2B-only, Java-only) was chosen for tractability and data-consistency reasons (see `Decision_Log.md` §2). If, once the model and data pipeline are further along, this scope turns out to not fit well — e.g., data patterns that only make sense with B2C included, or a network structure/coverage story that only makes sense with Sumatra back in — the fix should be to **re-open the scope decision**, not to keep patching/adjusting the data to force it into the current narrow scope. Repeatedly forcing fixes onto data that doesn't fit the chosen scope is a sign the scope itself needs revisiting, not the data.

**Trigger conditions to watch for (revisit scope if any of these show up):**
- Coverage (f2) or CO2 (f3) results look distorted or hard to interpret specifically because Sumatra customers/facilities are missing from the picture.
- B2B-only data leads to validation issues (e.g., a large chunk of ship-to groups' behavior only makes sense once B2C activity at the same locations is accounted for).
- The final candidate facility count (pending Java-only recount, `Decision_Log.md` §7) turns out too small to produce a meaningful Pareto frontier.

**Action if triggered:** revisit `Decision_Log.md` §2 (Scope Decisions), re-run the Java+Sumatra / B2C data checks already done earlier in this project's history, and update scope with full reasoning documented — not a silent workaround.

**Status:** not triggered yet — current scope (B2B-only, Java-only) still stands. This is a watch item, not an active task.
