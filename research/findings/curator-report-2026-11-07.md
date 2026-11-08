======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-11-07
Week of: 2026-11-02
Window used: 2026-10-31 to 2026-11-07 (researcher dateRange; includes the Oct 31 Canada configurator item)

[1/4] Category Findings Loaded
✓ 9 categories researched
✓ 26 keyChanges collected
✓ Lint-raw: 0 errors, 1 warning
  - warning COVERAGE_GAP on fsdv15: "FSD supervised fleet counter passes 17 billion miles" (addressed below; filed)

Quiet week: 4680 Battery Cell Production. skipReason is set and searchLog.queries is non-empty. No cell-output, yield, or GWh print. The 40 kWh Cybercab pack remark and the Berlin 18 GWh line were correctly left unfiled (future pack size; October Battery-News recap). Not a researcher failure.

[2/4] Deduplication
✓ Removed 1 duplicate

- Dropped "Musk ties a mid-2027 Cybertruck wind-down to Cybercab floor space" (Cybercab Production). Same source as the Vehicle Production item (https://teslanorth.com/2026/11/06/tesla-cybertruck-wind-down-cybercab-2027/). Owner kept: Vehicle Production & Delivery, which also carries the Nov 5 US price hike and states that no Cybercab rate was disclosed. The idle-line and "year-end deliveries are an aim" lines were already last week's Cybercab items, not a new production count. Cybercab authorizations staying at 573 are in the registration note, not a second keyChange.

No exact title+category matches versus last week's keyChanges.

Seen URLs: one accepted source was already in hotContext.seenUrls — https://altindex.com/ticker/tsla/job-posts. Kept as a genuine new reading. The live counter printed 2,393 on Nov 7 after 8,155 on Oct 29 and then 462 and 710, and it still conflicts with the page's own October figure of 7,445. That is not a recap of a prior hiring article. No company-wide job metric was filed from it.

[3/4] Sentiment Validation
✓ 0 sentiment corrections applied

No item had status=positive and reality=negative. Headline-positive items that are actually negative were already filed as status=negative (SI6 slide, v14.3.13 point build, Optimus rent and hand patent, Terafab cost talk, Littleton and FSD hiring, Canada Model 3 still not orderable). Headline-positive items whose reality is neutral were already status=neutral (Fort Worth, Austin cameras, Robotaxi app, RDW speed cap, Germany, Argentina, Korea imports, Norway, China incentives, the new 17 billion mile counter). AltIndex's scary live count was left neutral, not negative: the series is broken, which is not evidence of a hiring collapse.

[4/4] Quality Filter
✓ Rejected 1 weak claim

- "Owner clips flag v14.3.13 left-turn and Cybertruck regressions" (FSD v15 Software). single_outlet_anecdote_low_confidence. Tesla Oracle only, confidence low, social video, fault not established, no fleet rate. Not promoted into a keyChange or into fsdv15 criticalNews. The supervised point-build item still stands on the Not a Tesla App notes.

Coverage gaps
- FSD supervised fleet counter passes 17 billion miles | fsdv15 | filed
  Fetched https://teslanorth.com/2026/11/02/fsd-fleet-17-billion-miles/. In window (2026-11-02), not in seenUrls, and fsdv15 owns cumulative miles. The safety page showed more than 17.003 billion supervised miles and more than 6.757 billion city miles, about 300 million above the roughly 16.7 billion late-October print. Filed as neutral: still driver-supervised, counter steps at an average fleet rate, v15 not involved. The 75% North American attach line in that writeup is a Q3 figure, not a November software change.

Metrics
- robotaxiRegistered: filed 1,244 on 2026-11-01 (671 Model Y + 573 Cybercab). Texas DMV / TxMCCS authorization, unchanged through Nov 7. The +40 versus the Oct 30 print of 1,204 is all Model Y. Not moved onto robotaxiFleet or cybercab production.
- robotaxiFleet: none. Rejected 1,244 (statewide roster), 357 (community VIN matches), and 582 (VIN-match total).
- cybercab production: none. Rejected 573 (flat Cybercab authorization slice, not output) and 2,172 (unchanged VIN floor).
- cityFleet: none. No row whose basis is sighting-floor or company and whose count is new. Dropped unchanged 30-day floors (Austin 405, Dallas 70, Bay Area 721, as-of 2026-10-16). Dropped camera events and non-fleet counts: 33 southwest-of-fence detections, 27 north-of-fence engineering detections, 1,576 Halloween Austin camera events, 357 statewide matched-active VINs, and 145 (Fort Worth square miles, not vehicles). Fort Worth launched with no Tesla vehicle count, so no city row was invented.
- jobPostings: none. Rejected AltIndex 2,393 (discontinuous with ~8,155 / October 7,445), 7,445 (October monthly aggregate, not a new daily point), and RobotTraining slices 178, 175, and 31 (training/collector subsets, not the company-wide series).
- No quarterly production/delivery print. Q3 was already filed last week.
- Other rejected non-series figures: SI6 80x and 144 GB (targets / October memory cut), Taylor Fab 2 year 2030 (AMD/NVIDIA HBM, not Tesla wafers), Berlin 18 GWh and Cybercab 40 kWh (not cell output), Optimus 20,000/week and 10 million/year and the $30,000 build-cost remark, Terafab $1 trillion and the restated $16.8 billion phase one, FSD country count 10 (unchanged), TeslaFi 11.8% of one build, and a 1,650-car wave.

Category notes
- Cybercab: Fort Worth is a real Nov 2 Model Y city with no disclosed fleet or monitor count. Paid Cybercab remains Austin-only. Question 8 FMVSS documents are a full CBI withhold, not a violation finding. App 26.11.0 and outside-geofence cameras are scoped as UI and camera events, not a fleet expansion.
- FSD approvals: RDW tightened the existing Dutch file (10% speed margin, Assisted Driving name) and did not add a country. The Korean filing is a KFTC complaint, not a certification.
- FSD v15: 2026.38.5.12 repeats supervised v14.3.13 notes. v15 is still absent. Miles item filed from the coverage gap.
- Optimus: "probably rent" has no price, term, or date. The hand patent is a 2022 priority filing, not a production hand.
- AI chip: Nov 4 slide restates SI5/SI6 multipliers and leaves Dojo D3's node as TBA. Tom's Hardware's 2029–2030 window and wattage figures are not on the slide. No tape-out or yield.
- Terafab: trillion-dollar line is Baron's, and Musk did not fund it. Digitimes TSMC-operator report is unconfirmed (paywalled body; Benzinga says the companies did not comment) and was kept as a negative unconfirmed report, not as a deal. Governor-elect item is political risk around JETI, not a revoked abatement.
- Jobs: new seats are a Littleton data-collection shift lead and temporary supervised safety drivers / local supervisors, not an engineering ramp. Peabody fleet-support copies are not a Boston robotaxi launch.
- Production & delivery: Shanghai 67,829 is a real CPCA preliminary print (down 28.88% from September, no domestic/export split). Germany's 290.9% year-over-year jump is off a weak base and still trails BYD. Argentina is a Nov 20 date with no prices or orders.

======================================================================
✓ CURATION COMPLETE: 25 validated keyChanges
  4 trends
  0 sentiment corrections
  1 weak claim rejected
  1 cross-category duplicate removed
  1 coverage gap filed
  robotaxiRegistered 1,244; no in-service fleet or city row
======================================================================
