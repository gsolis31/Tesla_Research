# Tesla Curator — Validation Report
## 2026-09-19 (Week of 2026-09-14)

======================================================================

## [0] Lint Report — research/logs/2026-09-19/lint-raw.json

**0 errors, 2 warnings across 9 category files**

### Errors (must-drops) — 0

No lint-raw errors. Nothing dropped on mechanical gates (date window, title length, Electrek-only+low, evidence count, ownership trespass, registration-as-fleet).

### Warnings (judgment calls) — 2

| Category | Code | Detail | Action |
|----------|------|--------|--------|
| `fsd` | `COVERAGE_GAP` | Scout: "Tesla AUNZ: FSD Supervised logs 160 million km in first year with local safety scorecard" | **rejected-wrong-owner** — already filed under `fsdv15` (cumulative miles / software safety stats). See coverage gap section. |
| `productionDelivery` | `COVERAGE_GAP` | Scout: "Tesla deploys first Accordion Supercharger: 16 factory-preassembled stalls per truck" | **Filed** — fetched Electrek; distinct from last week's 1.2 MW Semi Megacharger. See coverage gap section. |

---

## [0b] Coverage Gaps — 2 from scout, all addressed

### 1. Tesla AUNZ: FSD Supervised logs 160 million km in first year with local safety scorecard
- **URL**: https://teslanorth.com/2026/09/18/tesla-fsd-160-million-km-australia-nz/
- **likelyCategory**: `fsd`
- **Decision**: **rejected-wrong-owner**
- **Reason**: Fetched TeslaNorth (Sarah Lee-Jones, Sept 18). Official Tesla Australia & New Zealand X posts celebrate one year of FSD Supervised with more than 160 million km (~4,000 laps around Earth) versus a ~2.4 billion km manual-with-Active-Safety baseline, claiming 40% fewer collisions (major+minor), 66% fewer AEB events, 90% fewer harsh braking events, and related intervention-proxy cuts. Tesla did not split AU vs NZ or disclose subscription counts. HW3 Lite for AU/NZ remains unpublished. AU/NZ have been live Supervised FSD markets since 2025 — this is cumulative miles and Tesla-defined software safety stats, not a new country approval. `fsdv15` researcher already filed the same official dataset from Not a Tesla App (plus Oceania 2026.28.5 / v14.3.9 OTA). `fsd` researcher correctly skipped the NATA URL as fsdv15-owned. Kept the existing `fsdv15` keyChange; did not re-file under FSD Country Approvals.

### 2. Tesla deploys first Accordion Supercharger: 16 factory-preassembled stalls per truck
- **URL**: https://electrek.co/2026/09/16/tesla-accordion-supercharger-deployment/
- **likelyCategory**: `productionDelivery`
- **Decision**: **filed**
- **Reason**: Fetched Electrek (Fred Lambert, Sept 16). Tesla Charging posted the first Accordion Supercharger: 16 V4 stalls fold onto one truck, 20% cheaper install, instant commission, between-space layout for lots that cannot trench a curb-behind cabinet. Stated goal: pre-assemble every Supercharger in a factory. Distinct from last week's factory-pre-assembled 1.2 MW Semi Megacharger hardware (different SKU, different URL, not in `seenUrls`). `productionDelivery` researcher did not consider the URL — a miss, not a successful skip. Filed as **neutral** at **medium** confidence: official Tesla Charging tweet is the primary source; Electrek is the only write-up. Connector growth remains ~17% YoY (82,357 connectors / 8,704 stations as of Q2 2026) versus 35–45% in 2020–21 after the April 2024 charging-team layoff. One site does not reverse that slowdown or move Q3 deliveries.

---

## [1] Category Findings Loaded

| Category | File | Status | Filed | Skip Reason |
|----------|------|--------|-------|-------------|
| AI Chip Production | findings-aiChip.json | **empty** | 0 | Valid quiet week: 14 queries. English follow-ups of Samsung Taylor AI5 trial production (already filed Sept 15) added no yield, sample, or shipment numbers. Intel 14A is an eight-company analyst list, not a Tesla chip milestone. Terafab coverage correctly routed out. |
| 4680 Battery Cell Production | findings-battery4680.json | **empty** | 0 | Valid quiet week: 10 queries. In-window Semi factory tour mentions 4680 pack architecture only — no Texas/Berlin cell GWh, yield, scrap, or dry-electrode update. |
| Cybercab Production | findings-cybercab.json | ok | 2 | — |
| FSD Country Approvals | findings-fsd.json | ok | 1 | AUNZ miles correctly skipped as fsdv15 |
| FSD v15 Software | findings-fsdv15.json | ok | 2 | — |
| Job Postings | findings-jobPostings.json | **empty** | 0 | Valid quiet week: 8 queries. AltIndex +58 / +0.7% is a metric tick only; mix still ~40% service/sales. No new AI/Optimus production-ramp hiring story. |
| Optimus Production | findings-optimus.json | ok | 2 | — |
| Vehicle Production & Delivery | findings-productionDelivery.json | ok | 4→5 | Accordion Supercharger added from coverage gap |
| Terafab In-House Chip Manufacturing | findings-terafab.json | ok | 1 | — |

**12 keyChanges collected from researchers** + **1 coverage-gap filing** = **13 after curation**

Quiet categories (`aiChip`, `battery4680`, `jobPostings`) all have non-empty `searchLog.queries` — not researcher failures.

---

## [2] Deduplication

Checked all 13 stories against:
- `hotContext.lastWeekKeyChanges` (17 entries from 2026-09-16 mid-week package)
- `hotContext.seenUrls` (canonical list in curator config)
- Within-week de-overlap (title+category and same-URL)

**Result: 0 duplicates removed**

Same-week (weekOf 2026-09-14) but substantively new vs last package:
- Cybercab 58 VINs vs last week's frozen-at-49 / NHTSA Special Order / rider-report / China-display set
- v14.3.10 vs last week's v14.3.9 changelog
- AUNZ 160M km vs last week's UK branding law
- Barclays 475k vs last week's Goldman 435k cut (contradicts, does not recap)
- Forum Mobility public Megachargers vs last week's pre-assembled 1.2 MW Megacharger hardware
- Roadster $50k deposits vs last week's Oct 1 Waco reveal date
- Ningbo supplier-audit denials vs last week's unofficial 15,000-unit supply-chain target
- Accordion Supercharger URL was not in `seenUrls`

---

## [3] Sentiment Validation

### Auto-corrections applied: 0

No `status=positive` + `reality=negative` mismatches. Researchers already filed the two hardest stories as negative (Barclays "beat" that is still below Q2; Roadster deposits with no SOP; Ningbo audit headlines that named vendors denied).

### Warning-level sentiment flags (no auto-correction): 2

| Category | Title | Flag | Action |
|----------|-------|------|--------|
| FSD Country Approvals | Flemish Minister Presents Tesla-Supplied Belgian FSD Stats… | `status=neutral` / `reality=negative`; 4 neg vs 3 pos | **Kept neutral.** Parliamentary presentation of Tesla-supplied stats is not a new approval and not a new harm. Negative reality is the unchanged TCMV 9%-vs-65% math — ongoing, not a this-week regression. Status=positive would have been sugar-coating and was not used. |
| FSD v15 Software | FSD v14.3.10 (2026.27.10): identical notes to v14.3.9, 0.2% TeslaFi | `status=neutral` / `reality=negative`; 5 neg vs 3 pos | **Kept neutral.** Copy-paste OTA is a non-event, not a software regression. ACE remains in the HW4 notes. Negative reality correctly flags that v15 is still unshipped two weeks before the October robotaxi target. |

Other stories have more negative than positive *signals* with `status=neutral` — that is the intended anti-sugar-coating pattern (caveats outnumber headlines; overall week direction is not a loss). Not auto-corrected.

Cybercab 58 kept `confidence=low` (single published source; TeslaOracle still cited 49 the same day). Not Electrek-only, so it clears the weak-claim gate.

---

## [4] Quality Filter

### Weak claims rejected: 0 researcher stories

All 12 researcher stories plus the Accordion filing have:
- ≥2 total evidence signals ✓
- Source quality appropriate for their confidence level ✓
- Not Electrek-only + low-confidence combinations ✓

### Notes on borderline cases:

**cybercab 58 VINs** (TeslaNorth, confidence low): Registration, not paid dispatch. Correctly **not** written to `metrics.cybercab` or `metrics.robotaxiFleet`. Researcher rejected 58 / 448 as registry counts. Kept as pipeline news only.

**cybercab first-responder video** (TeslaOracle + official Robotaxi clip): Ops hygiene / PR, not a fleet or certification win. Status correctly neutral. Kept because it is new official content in-window after unsupervised Austin launch.

**Accordion Supercharger** (Electrek-only write-up of Tesla Charging tweet): Filed at medium confidence, not low. Official Tesla Charging post is the primary source. Distinct from last week's Semi Megacharger.

**terafab CSISD briefing** (The Eagle): Neighboring-district housing/CTE briefing with no vote, no Grimes tax revenue, and no construction/permit update. Medium confidence. Kept as the only in-window terafab-owned local-politics item; not a fab milestone.

**optimus Ningbo** (SCMP + Yicai denials + Bloomberg): Highest-quality Optimus story this window. Status negative is correct — named vendors denied new inspections; unofficial 15k vs 50k vs 5k volume figures conflict; Tesla silent.

---

## [5] Category Ownership Enforcement

| Story | Filed Under | Correct? | Action |
|-------|-------------|----------|--------|
| AUNZ 160M km / 40% fewer collisions | fsdv15 | ✓ cumulative miles + HW3/HW4 software ceiling | Kept (scout wanted fsd) |
| Flemish/Belgian Tesla-supplied stats + TCMV | fsd | ✓ country / EU homologation politics | Kept |
| v14.3.10 (2026.27.10) copy of v14.3.9 notes | fsdv15 | ✓ OTA version | Kept |
| Texas Cybercab 58 VINs + first-responder training | cybercab | ✓ robotaxi fleet/ops | Kept |
| Giga Texas Optimus steel + Ningbo supplier audits | optimus | ✓ | Kept |
| Barclays Q3, Forum Mobility, Roadster deposits, Tokyo subsidies, Accordion | productionDelivery | ✓ volume / charging-adjacent vehicle stories | Kept |
| CSISD Terafab housing spillover | terafab | ✓ school boards / local politics | Kept |
| Samsung Taylor AI5 recaps / Intel 14A listicle | aiChip skip | ✓ no new chip milestone | Quiet week honored |
| App 4.61.0 Optimus Energy strings | skipped by optimus | ✓ dormant app hooks, not production | OK |

No same-URL duplicates across categories. No ownership trespasses in accepted keyChanges (lint-raw would have errored on classic patterns).

---

## [6] Data Normalization

### Category names normalized:
All 13 keyChanges use canonical labels:
- Cybercab Production ✓
- FSD Country Approvals ✓
- FSD v15 Software ✓
- Optimus Production ✓
- Vehicle Production & Delivery ✓
- Terafab In-House Chip Manufacturing ✓

### Status / confidence / dates:
- Status values: positive | negative | neutral only ✓
- Confidence: high | medium | low only ✓ (one `low`: Cybercab 58)
- Dates fall in weekOf 2026-09-14 through date 2026-09-19 ✓
  - Earliest: 2026-09-16 (Accordion)
  - Latest: 2026-09-19 (v14.3.10)
- Titles ≤ 120 characters ✓
- `impact` fields stripped from researcher output ✓

### Curated lint:
`python3 scripts/lint_findings.py --curated research/findings/2026-09-19.json` → **0 errors, 0 warnings**

---

## [7] Trends Extracted

4 trends from 13 validated keyChanges across 6 active categories:

1. **Vehicle Production & Delivery**: Street split 435k–475k for Q3, and even Barclays' raise is still below Q2 480k; Roadster deposits and charging prefab do not move volume
2. **Optimus Production**: Giga Texas steel nears the north beam, but named China vendors denied this week's audit headlines — Tesla still discloses zero units
3. **Cybercab Production**: Texas registry +9 to 58 is a DMV roster, not paid dispatch; NHTSA sworn FMVSS answers remain due September 30
4. **FSD software and regulatory**: v14.3.10 copies v14.3.9 notes at 0.2% TeslaFi; Belgium's Tesla-supplied stats do not change the Oct 6 TCMV 9%-vs-65% math

---

## [8] Metrics & Category Updates

### Metrics included in output:

| Series | Count | Date | Notes |
|--------|-------|------|-------|
| `jobPostings` | 7,892 | 2026-09-19 | AltIndex live count; +58 / +0.7% vs Sept 16 (7,834). Mix unchanged: ~40% service/sales vs 8% engineering / 6% autonomy. |

### Metrics NOT included:

| Series | Reason |
|--------|--------|
| `cybercab` | 58 is TxDMV / FSD Database registration, not production. VIN floor remains 2,172. Rejected by researcher; honored. |
| `robotaxiFleet` | 58 Cybercabs and 448 combined Tesla Robotaxi authorization are registry counts, not active paid dispatch. Rejected. |
| `optimus` | Unofficial 15k / 50k / 5k 2026 figures conflict; Tesla has disclosed zero units. Rejected. |
| `quarterlyData` | Barclays 475k and Goldman 435k are analyst estimates, not Tesla IR. Official Q3 P&D due around October 2. |

### Category Updates:
7 categories with `latestStatus` / `nextMilestone` / `concerns`:
- cybercab, fsd, fsdv15, jobPostings, optimus, productionDelivery (patched to mention Accordion), terafab
- `aiChip` and `battery4680` omitted (researcher `categoryUpdate: null` — valid quiet weeks; last week's criticalNews stands)

---

## [9] Validation Summary

| Metric | Count |
|--------|-------|
| Researcher keyChanges collected | 12 |
| Lint error drops (must-drops) | 0 |
| Coverage gaps addressed | 2 |
| Coverage gaps filed | 1 |
| Coverage gaps rejected | 1 (`rejected-wrong-owner`) |
| Duplicates removed (vs last week + seenUrls) | 0 |
| Sentiment auto-corrections | 0 |
| Weak claims rejected | 0 |
| **Final validated keyChanges** | **13** |

---

## [10] Output Written

- **Findings**: `research/findings/2026-09-19.json`
  - 13 validated keyChanges across 6 categories (aiChip, battery4680, jobPostings quiet)
  - 4 trends
  - 1 metric update (jobPostings: 7,892)
  - 7 categoryUpdates
  - 2 coverage gap dispositions in metadata
  - 15 canonical urlsSeen (13 sources + 2 corroborating: TeslaNorth AUNZ, Yicai supplier denials)

- **This report**: `research/findings/curator-report-2026-09-19.md`

======================================================================
✓ CURATION COMPLETE: 13 validated keyChanges | 6 active categories | 0 duplicates | 0 sentiment corrections | curated lint 0/0
======================================================================

### Critical issues for next week's researcher attention:
1. **NHTSA Sept 30 deadline** — Tesla's sworn FMVSS compliance response for Cybercab (Special Order). Outcome determines legal path to scale.
2. **NHTSA EA26002 partial response due Sept 23** — FSD investigation clock, separate from Cybercab AQ26002.
3. **EU TCMV October 6 vote** — Six small states still ~9% of EU population vs 65% threshold. Watch France/Germany/Italy/Spain.
4. **FSD v15 fleet deployment** — Elluswamy's October commercial-robotaxi target. v14.3.10 shipped with no new FSD model.
5. **Q3 delivery report around October 2** — Street is 435k (Goldman) to 475k (Barclays) vs Q2 official 480,126.
6. **Roadster October 1 Waco reveal** — $50k refundable deposits are live; still no SOP/delivery date.
7. **Terafab** — Dec. 1 JETI start still paper; W.D. Tex. 1:26-cv-02543 trademark docket and records TRO remain without a hearing date.
