======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-09-26
Week of: 2026-09-21
Output: research/findings/2026-09-26.json

[1/6] Category findings loaded
✓ 9 categories researched
✓ 23 raw keyChanges collected
✓ aiChip filed nothing, with a skipReason and a non-empty searchLog (valid quiet week)
✓ Lint-raw: 0 errors, 1 warning (COVERAGE_GAP on cybercab). No must-drops.

[2/6] Deduplication
✓ Removed 1 same-URL cross-category duplicate
✓ 0 exact title+category duplicates vs last week
✓ 1 seenUrl kept as a new reading (job-postings tracker), not as a new story

Same-URL duplicate
- Dropped Cybercab "First in-house-cathode Cybercab is a single unit, not a volume ramp"
- Kept 4680 "First Cybercab uses Giga Texas nickel cathode; still no 4680 output figure"
- Owner is 4680 Battery Cell Production. Same Teslarati URL. The 10-second drive-unit line was a recruiting takt, not finished vehicles, and was not refiled.

Seen URL, kept as a new print
- Job Postings source https://altindex.com/ticker/tsla/job-posts was already seen when the index crossed 7,000.
- The Sept 26 reading is 8,001, up 109 / +1.4% from 7,892 on Sept 19, with the same service-heavy mix. Filed as neutral, not as an AI hiring wave.

Not duplicates (new developments, different title and URL)
- Texas Cybercab authorizations 58 → 126 (last week stopped at 58)
- FSD v14.3.10 on 2026.27.11 is a wide wave; last week was the 0.2% 2026.27.10 drip
- Sanhua/Joyson Global Times denial on Sept 22 follows a new "certified partner / ~5,000 units" escalation. Last week's item was the Sept 18 SCMP audit story. Different URL.
- UBS 470k is not the filed Goldman 435k or Barclays 475k notes
- Semi factory inauguration is not last week's IAA debut or Megacharger items
- Czechia and the Oct 6 non-vote are not last week's UK branding item or the Flemish minister's Tesla-supplied stats
- Brussels speeding study is not those Tesla-supplied Belgian stats

[3/6] Sentiment
✓ 0 status corrections. No accepted item had status=positive and reality=negative.
✓ Researchers had already set status to negative wherever reality was negative and the headline was positive (Cybercab roster, Optimus ramp, supplier denials, Semi inauguration, China discounts, UBS, Terafab permit freeze). Those were checked and left negative.
✓ Neutral items whose headlines are friendlier than reality (Czechia, Gen 3 app art, HW3 S/X Lite, cathode photo, Austin slab, job count) stay neutral. They are real but small.
✓ TERA-print confidence raised from low to medium. Service and the Oct 9 answer date are on the docket. Reality stays negative: no ruling.

[4/6] Quality filter
✓ Rejected 1 weak claim
✓ Rejected 1 out-of-window claim

Weak
- "First Automatic Collision Evasion clip re-engages FSD during a deliberate lane change" (FSD v15). One Reddit dashcam via Not a Tesla App, confidence low, no Tesla statement. The feature was already in the v14.3.9 notes filed last week. A single takeover fight is not a new software version.

Out of window
- "Houston Cybercab lot is steering-wheel prototypes, not a paid launch". Article date 2026-09-20 is before weekOf 2026-09-21 (curated lint window). Also confidence low, no vehicle count, and a single Tesla Oracle video of steering-wheel prototypes. Not redated.

[5/6] Coverage gaps
- Austin robotaxi active count falls back to 8 vehicles after the Cybercab launch spike
  - likelyCategory: cybercab
  - decision: rejected-weak
  - Fetched https://electrek.co/2026/09/22/tesla-robotaxi-active-fleet-austin-crashes-8-vehicles/ (Fred Lambert, Sept 22).
  - Electrek-only. It cites a Robotaxi Tracker chart: 7-day Austin passenger-carrying count back to 8, and a registered fleet of 476 (409 Model Y + 67 Cybercabs).
  - The tracker page did not return a body in this week's cybercab research. The Sept 26 community scrape tagged about 44 Cybercabs, which is a different cut, and the column does not reconcile the two.
  - The registration-versus-activity gap is already filed from the Sept 26 roster (126 authorized vs about 44 tagged). Count 8 was not written to robotaxiFleet.

[6/6] Metrics and category updates
✓ jobPostings: 8001 on 2026-09-26 (AltIndex). JobzMall 8,266 was not used.
✓ cybercab: [] — 126, 546, 67, 44, and the Electrek 8 are not production and not in-service fleet
✓ robotaxiFleet: [] — same. No robotaxiRegistered point either; hot context does not define that series, so a Cybercab-only 126 was not spliced onto it.
✓ quarterlyData: [] — UBS 470k, Visible Alpha ~454k, Semi nameplate 50,000, and ZET SCALE 2,500 are not a Tesla P&D print
✓ No Optimus unit metric. "Several hundred a week" is anonymous and unconfirmed.
✓ FSD country count of 7 stays in the Czechia keyChange. Merge does not accept an fsdApprovals series from findings.
✓ Category updates written for the eight categories with accepted news. aiChip left untouched (quiet week; do not invent a chip update).

Ownership
- Cathode tie-in kept under 4680, not Cybercab
- EU vote, Czechia, and the Brussels speed study kept under FSD Country Approvals
- OTA wave, camera-bug, and HW3 S/X Lite kept under FSD v15 Software
- No AI5 item under Terafab. aiChip's in-window hits were recaps of the Sept 15 Samsung Taylor trial start.

Quiet week
- aiChip: no new primary update on AI5/AI6 yield, tape-out, TSMC samples, or Dojo. In-window copy restated the already-filed Sept 15 trial start.

======================================================================
✓ CURATION COMPLETE: 20 validated keyChanges
  raw 23 → accepted 20
  duplicates removed 1
  sentiment corrections 0
  weak claims rejected 1
  out of window 1
  coverage gaps filed 0 / rejected 1
  curated lint: 0 errors, 0 warnings
======================================================================
