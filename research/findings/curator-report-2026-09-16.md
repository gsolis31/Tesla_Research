# Tesla Curator — Validation Report
## 2026-09-16 (Week of 2026-09-14)

======================================================================

## [0] Lint Report — research/logs/2026-09-16/lint-raw.json

**1 error, 8 warnings across 9 category files**

### Errors (must-drops) — 1

| Category | Code | Title | Action |
|----------|------|-------|--------|
| `fsd` | `OWNERSHIP_TRESPASS` | "Tesla Spain FSD Regulatory Testing Reaches 460,000 km Over Two Years — No Customer Approval in Sight" | **DROPPED** — description mentioned `v14.3.7` and `HW3 on v14.1 Lite` (triggers fsdv15 regex pattern). The underlying story (Spain regulatory testing milestone under ES-AV framework) is genuinely fsd-owned, but lint-raw errors are must-drops per contract. Spain testing context preserved in fsd `categoryUpdate.concerns`. |

### Warnings (judgment calls) — 8

| Category | Code | Detail | Action |
|----------|------|--------|--------|
| `cybercab` | `COVERAGE_GAP` | Scout: "Tesla Cybercab turns 10-minute Austin trip into 70-minute detour" | **Filed** — fetched article; fleet-wide no-highway/railroad constraint is distinct from researcher's second-week rider report. See coverage gap section. |
| `optimus` | `TITLE_TOO_LONG` | 134 chars (max 120) | **Truncated** → "Optimus 2026 target: supply chain cites 15,000 units with weekly ramp milestones — no official Tesla verification" (113 chars) |
| `fsdv15` | `TITLE_TOO_LONG` | 126 chars (max 120) | **Truncated** → "FSD v14.3.9 (2026.27.6): MLIR 2 compiler rewrite, 20% faster reaction time, Automatic Collision Evasion on HW4" (111 chars) |
| `fsdv15` | `TITLE_TOO_LONG` | 128 chars (max 120) | **Truncated** → "Elluswamy: FSD v15 targeting commercial robotaxi fleet in October; 24/7 operations contingent on deployment success" (115 chars) |
| `productionDelivery` | `COVERAGE_GAP` (×3) | Megachargers, Roadster Oct 1, Roadster Cyber redesign | See coverage gap section — 2 filed, 1 rejected |
| `terafab` | `COVERAGE_GAP` | Scout: "Tesla and SpaceX sue nanotechnology firm TERA-print" | **Filed** — Reuters Tier 1 source. See coverage gap section. |

---

## [0b] Coverage Gaps — 5 from scout, all addressed

### 1. Tesla Cybercab turns 10-minute Austin trip into 70-minute detour
- **URL**: https://electrek.co/2026/09/14/tesla-cybercab-70-minute-austin-detour/
- **Decision**: **filed**
- **Reason**: Fetched article (Electrek, Fred Lambert, Sept 14). Confirms fleet-wide constraint: Tesla Austin robotaxis cannot use highways (MoPac, US-183) or cross at-grade railroad crossings. Rider's 10-minute trip (99 Ranch → Domain) became 70 minutes routed south through East Austin to avoid Capital Metro Red Line grade crossings. Applies to ALL Austin Tesla robotaxis (Cybercab + Model Y), not just the new vehicle. Contrast: Waymo already runs on freeways. Tesla app shows price not time estimate. Tesla crash rate ~1/57k miles (~4× worse than human). Electrek is Tier 2 (known critical bias) but confidence is medium — no-highway routing is independently corroborated by multiple Reddit riders and the researcher's own filed story (which mentions the 70-min Reddit detour as a negative signal). The fleet-wide, cause-explained framing is substantively distinct from the researcher's second-week service-quality story. Filed as "Austin Cybercab fleet avoids highways and at-grade railroad crossings — turns 10-minute trips into 70-minute detours."

### 2. Tesla and SpaceX sue nanotechnology firm TERA-print to secure 'Terafab' trademark
- **URL**: https://www.reuters.com/legal/legalindustry/tesla-spacex-sue-nanotech-company-over-terafab-name-2026-09-16/
- **Decision**: **filed**
- **Reason**: Reuters Tier 1 source. Federal declaratory judgment complaint filed Sept 16 in U.S. District Court for the Western District of Texas (No. 1:26-cv-02543). TERA-print (Illinois, photolithography printer) sent a C&D in June 2026 over its existing "Tera-Fab" trademark. Settlement talks continued through Sept 2 then broke down; TERA-print vows to "vigorously defend." Tesla applied for 3 "Terafab" USPTO trademarks in May 2026. Outcome: a loss or forced rebrand would disrupt the $16.8B project's communications and permitting track. Real new legal risk not previously filed. Filed as "Tesla and SpaceX file declaratory suit to keep 'Terafab' name — TERA-print's cease-and-desist prompted preemptive federal action."

### 3. Tesla deploys first pre-assembled 1.2 MW Megachargers for Semi production ramp
- **URL**: https://teslanorth.com/2026/09/16/tesla-preassembled-megachargers-semi-ramp/
- **Decision**: **filed**
- **Reason**: Official Tesla Charging X announcement confirmed by TeslaNorth (Sept 16). First factory-pre-assembled V4 cabinet + dual-post Megacharger units (1.2 MW/post) physically in the field. Concrete infrastructure milestone directly supporting Semi production ramp. Aligns with IAA Semi debut (Sept 14, filed by researcher) and Sept 24 Sparks factory rollout event. Filed as "Tesla Charging deploys first factory-pre-assembled 1.2 MW Megachargers to support Semi production ramp." (status: positive — actual hardware deployment confirmed)

### 4. Tesla Roadster production reveal confirmed for October 1 in Waco, Texas
- **URL**: https://evwire.com/p/tesla-roadster-launch-teaser-secret-message-explained
- **Decision**: **filed**
- **Reason**: Fetched EVwire article (Simon Alvarez, Sept 14). First hard date in nine years: Tesla website countdown to Oct 1 now live; RSVP invitations sent to reservation holders listing Waco TX, RSVP deadline Sept 16, ID checks. Musk: "Excitement guaranteed." Two versions confirmed: street-legal Roadster + non-street-legal SpaceX thruster variant. Oct 1 is a reveal, not a delivery. Filed as neutral: meaningful milestone (hard date after 9 years) but not a delivery commitment. Filed as "Tesla Roadster reveal set for October 1 in Waco, Texas — first hard date after nine years of delays."

### 5. Tesla Roadster teaser hints at 'Cyber' redesign — full-width light bar and angular styling
- **URL**: https://electrek.co/2026/09/15/tesla-roadster-cyber-treatment-redesign/
- **Decision**: **rejected-weak**
- **Reason**: Fetched Electrek article (Fred Lambert, Sept 15). Primarily editorial opinion on Tesla's design choices ("it doesn't need a redesign; it needed to ship"). Design details (full-width light bar, angular styling) are inferences from a teaser image, not confirmed Tesla specs. Electrek-only source with no Tier 1 corroboration of specific design claims. Roadster Oct 1 reveal is already filed (gap 4 above) from EVwire, which covers the confirmed facts. The Electrek piece adds critical framing but does not meet the 2-source evidence bar for a new keyChange.

---

## [1] Category Findings Loaded

| Category | File | Status | Filed | Skip Reason |
|----------|------|--------|-------|-------------|
| AI Chip Production | findings-aiChip.json | ok | 1 | — |
| 4680 Battery Cell Production | findings-battery4680.json | **empty** | 0 | No new verified 4680 production news (GWh, yield, dry electrode) in Sept 12–16 window. Only candidate (basenor Cybertruck charging, Sept 13) is a vehicle story with single unverified secondary source for the 4680 claim. Valid quiet week with 8 search queries documented. |
| Cybercab Production | findings-cybercab.json | ok | 3 | — |
| FSD Country Approvals | findings-fsd.json | lint_error | 2→1 | Spain 460k km story dropped (OWNERSHIP_TRESPASS) |
| FSD v15 Software | findings-fsdv15.json | ok | 2 | — |
| Job Postings | findings-jobPostings.json | ok | 2 | — |
| Optimus Production | findings-optimus.json | ok | 1 | — |
| Vehicle Production & Delivery | findings-productionDelivery.json | ok | 2 | — |
| Terafab In-House Chip Manufacturing | findings-terafab.json | ok | 1 | — |

**13 keyChanges collected from researchers** (14 pre-lint, 1 dropped)

---

## [2] Deduplication

Checked all 13 researcher stories against:
- `hotContext.lastWeekKeyChanges` (17 entries from week of 2026-09-06/09)
- `hotContext.seenUrls` (544 URLs)
- Within-week de-overlap

**Result: 0 duplicates removed**

All stories represent genuinely new developments:
- aiChip: Last week = "fully booked + yield 80%" → this week = "trial production actually started Sept 15" ✓ new
- fsdv15: Last week = "v14.3.9 enters EAP rollout" → this week = "full MLIR 2 changelog" ✓ new detail not in last week's entry
- fsdv15: Last week = "Elluswamy previews v15 safety promise" → this week = "specific October fleet target, 24/7 ops conditional" ✓ new commitment
- optimus: Last week = "5,000 component batch order" → this week = "15,000-unit 2026 total with weekly ramp milestones" ✓ new consolidation
- All cybercab, fsd, jobPostings, productionDelivery, terafab stories: verified new URLs and substantively distinct content ✓

---

## [3] Sentiment Validation

### Auto-corrections applied: 1

| Category | Title | Original Status | Corrected To | Reason |
|----------|-------|----------------|--------------|--------|
| Optimus Production | "Optimus 2026 target: supply chain cites 15,000 units..." | `neutral` | **`negative`** | `sentiment.reality = "negative"`. Evidence ratio: 4 positive signals vs 9 negative signals. JPMorgan found tarped floor area with zero working robots in August. Polymarket commercial launch odds at 9% (down from 33%). No official Tesla unit count ever disclosed. Q2 IR capacity table shows "Construction" not "Production." 15,000 units is a >90% downgrade from Musk's 2024 "hundreds of thousands" forecast. |

### Warning-level sentiment flags (no auto-correction applied): 0

Remaining stories checked — no additional positive/negative mismatches found. Several stories are neutral with negative reality (e.g., cybercab rider report, fsd UK law), which is appropriate: the `status` field reflects overall week sentiment direction and not every story warrants a full negative designation when the data is genuinely mixed.

---

## [4] Quality Filter

### Weak claims rejected: 0 researcher stories

All 13 researcher stories that survived lint have:
- ≥2 total evidence signals ✓
- Source quality appropriate for their confidence level ✓
- Not Electrek-only + low-confidence combinations ✓

### Notes on borderline cases:

**optimus** (Motley Fool, allthings-elon.com): Both are secondary/aggregator sources citing supply chain channel checks. Confidence set to "medium" not "high" — appropriate given JPMorgan's contradicting floor visit. Filed but status corrected to negative.

**jobPostings gears** (diversityjobs.com / justjobs.com): Aggregator job board sources, posting dates may lag. Confidence "medium." Filed with appropriate caveats in description.

**cybercab highway constraint** (coverage gap, Electrek): Filed at medium confidence because no-highway routing is independently confirmed by multiple rider accounts and the researcher's own story. Not Electrek-only in substance.

---

## [5] Category Ownership Enforcement

### Cross-category issues reviewed:

| Story | Filed Under | Correct? | Action |
|-------|-------------|----------|--------|
| Spain FSD 460k km (v14.x references) | fsd | Lint says fsdv15 | DROPPED (lint error) |
| NHTSA Cybercab Special Order | cybercab | ✓ (FMVSS/vehicle cert = cybercab, not fsd) | Kept |
| EU recall remedy UNECE Reg 135 (fsdv15 researcher skipped) | fsdv15 → fsd | ✓ fsdv15 correctly self-skipped | OK |
| Tesla Semi IAA debut | productionDelivery | ✓ Semi = volume-adjacent vehicle production | Kept |
| Megacharger infrastructure (coverage gap) | productionDelivery | ✓ Semi charging = production ramp support | Kept |
| Terafab Taiwan insurance framing | terafab | ✓ Musk strategy = terafab, not aiChip | Kept |
| Terafab trademark suit | terafab | ✓ Legal dispute about the fab brand = terafab | Kept |

No cross-category trespasses found in accepted keyChanges.

---

## [6] Data Normalization

### Category names normalized:
All keyChanges verified against canonical category names:
- "AI Chip Production" ✓
- "Cybercab Production" ✓
- "FSD Country Approvals" ✓
- "FSD v15 Software" ✓
- "Job Postings" ✓
- "Optimus Production" ✓
- "Vehicle Production & Delivery" ✓
- "Terafab In-House Chip Manufacturing" ✓

### Status validation:
All 17 keyChanges use valid status values (positive/negative/neutral) ✓

### Confidence validation:
All sentiment.confidence values are "high" or "medium" — no "low" confidence items in final output ✓

### Date validation:
All keyChange dates fall within or immediately adjacent to the Sept 12–16, 2026 window ✓
- Earliest: 2026-09-12 (fsdv15 v14.3.9 changelog)
- Latest: 2026-09-16 (several stories)

---

## [7] Trends Extracted

4 trends derived from 17 validated keyChanges across 8 active categories:

1. **Cybercab Production** (4 negative/neutral keyChanges): NHTSA Special Order and fleet-wide routing constraints (no highways, no railroad crossings) create the most significant scaling headwinds since Austin launch
2. **Vehicle Production & Delivery** (4 mixed keyChanges): Goldman Sachs Q3 forecast cut to 435k (−9% vs Q2) signals the weakest quarter since Q1 2026; Roadster Oct 1 reveal and Megacharger deployment offer forward narrative but no near-term volume
3. **Optimus Production and Terafab** (3 keyChanges): Both categories marked by ambitious supply chain claims and strategy framing but zero official output verification and growing legal friction (trademark suit, records lawsuit)
4. **FSD Software and Regulatory** (3 keyChanges): v15 October commercial fleet target provides near-term catalyst; UK branding ban and EU TCMV vote failure risk compound the regulatory picture

---

## [8] Metrics & Category Updates

### Metrics included in output:

| Series | Count | Date | Notes |
|--------|-------|------|-------|
| `jobPostings` | 7,834 | 2026-09-16 | AltIndex live count; up 57% from July. LinkedIn US band: "7,000+" |

### Metrics NOT included:

| Series | Reason |
|--------|--------|
| `cybercab` | Fleet count is TxMCCS registry (49 Cybercabs) — registration count, not production metric. Rejected. |
| `robotaxiFleet` | Total TxMCCS 439-vehicle roster (Cybercab + Model Y mixed) — not active dispatch fleet. Rejected. |
| `optimus` | Supply chain target (15,000/year; 1,000/week) is unverified aspirational rate. No official disclosure. Rejected. |
| `fsd` (approvals count) | Slovenia (count→7) was last week's finding; source URL is in seenUrls. fsd metricUpdate not mapped to standard metrics series (cybercab/robotaxiFleet/jobPostings). Included in fsd categoryUpdate.latestStatus instead. |

### QuarterlyData:
None. Q3 2026 official delivery report due October 2, 2026 — not yet published. Goldman's 435k estimate is analyst forecast, not Tesla IR.

### Category Updates:
All 9 categories provided — 8 with updated latestStatus/nextMilestone/concerns; battery4680 set to `null` (valid quiet week with documented search activity).

---

## [9] Validation Summary

| Metric | Count |
|--------|-------|
| Researcher keyChanges collected | 14 |
| Lint error drops (must-drops) | 1 |
| Coverage gaps addressed | 5 |
| Coverage gaps filed | 4 |
| Coverage gaps rejected | 1 |
| Duplicates removed (vs last week + seenUrls) | 0 |
| Sentiment auto-corrections | 1 |
| Titles truncated (lint warnings) | 3 |
| Weak claims rejected | 0 |
| **Final validated keyChanges** | **17** |

---

## [10] Output Written

- **Findings**: `research/findings/2026-09-16.json`
  - 17 validated keyChanges across 8 categories (battery4680 quiet week)
  - 4 trends
  - 1 metric update (jobPostings: 7,834)
  - 9 categoryUpdates (1 null for battery4680)
  - 5 coverage gap dispositions in metadata
  - 22 canonical urlsSeen

- **This report**: `research/findings/curator-report-2026-09-16.md`

======================================================================
✓ CURATION COMPLETE: 17 validated keyChanges | 8 active categories | 0 duplicates | 1 sentiment correction
======================================================================

### Critical issues for next week's researcher attention:
1. **NHTSA Sept 30 deadline** — Tesla's sworn FMVSS compliance response for Cybercab. Outcome determines legal path to scale.
2. **EU TCMV October 6 vote** — Near-certain failure at 9% population coverage. Watch for last-minute country commitments or procedural postponement.
3. **FSD v15 fleet deployment** — Elluswamy's "next month or so" October target. Any slip pushes consumer rollout to 2027.
4. **Q3 delivery report October 2** — Goldman projects 435k; consensus 456k. Watch for actual Tesla IR report.
5. **Roadster October 1 reveal** — Waco TX event; first hard date in 9 years.
6. **Terafab trademark litigation** — TERA-print vows to vigorously defend. Watch for preliminary injunction filing.
