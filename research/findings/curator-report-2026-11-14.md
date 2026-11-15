======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-11-14
Week of: 2026-11-09
Research window used for dates: 2026-11-07 to 2026-11-14

[1/4] Category Findings Loaded
- 9 categories researched, all with search logs. None were empty.
- 25 researcher keyChanges collected.
- Lint-raw: 0 errors, 1 warning. The warning was COVERAGE_GAP on the Texas registry / Waymo story. No must-drop error codes (no REGISTRATION_AS_FLEET, OWNERSHIP_TRESPASS, STALE_DATE, ELECTREK_ONLY_LOW, or INSUFFICIENT_EVIDENCE).

[2/4] Deduplication
- Removed 0 duplicates.
- Checked exact title + category against last week's 24 keyChanges, exact source URLs against hotContext.seenUrls, and title + category inside this week.
- Near-misses kept because they are new developments, not the same item: Europe 2026.39.100 implements the speed cap (FSD v15 Software), while last week’s RDW cap stays under FSD Country Approvals; 2026.38.5.13 is a new build that still ships v14.3.13, not a repeat of 2026.38.5.12; Korea’s incomplete China-built exemption file is not last week’s KFTC marketing complaint; Cybertruck refunds and the summer-2027 extension are later than the Nov. 6 wind-down.

[3/4] Sentiment Validation
- Auto-corrected 0 items. Nothing was filed as status=positive with reality=negative.
- Judgment left in place: "New robotaxi reqs are city managers and night-shift staff, not autonomy engineers" has status=neutral and reality=negative (4 negative signals, 2 positive). Headline is already positive against a negative reality, so the mismatch is visible. Status was not flipped to negative: the reqs are a real city-ops buildout, not an autonomy hiring ramp and not a failed launch. The auto-fix rule covers only positive status paired with negative reality.

[4/4] Quality Filter
- Rejected 0 researcher keyChanges for Electrek-only + low confidence, fewer than 2 evidence signals, or 3+ vague words at low confidence.
- Kept the Grimes acreage item despite confidence=low. The source is KBTX on appraisal records and a Nov. 9 amended petition, the vague-word count is 0, and the negative reality already says acres are not a fab.
- Kept the Chicago Semi item. It is one TeslaNorth article quoting Tesla’s own Semi account, status and reality are neutral, and the evidence says handover is unconfirmed.
- Kept the J.P. Morgan Optimus note. Reuters names Tesla and still gives Optimus no volume, price, or customer. Status is already negative.

Coverage gaps
- filed — "Texas registry lists 1,302 Tesla Robotaxis, including 573 Cybercabs, just ahead of Waymo" (cybercab). Fetched https://www.teslarati.com/tesla-overtakes-waymo-texas-robotaxi-fleet-performs-shock-flip/. Nov. 10 print is 1,302 Tesla vehicles (729 Model Y + 573 Cybercab) versus Waymo 1,297. Filed under Cybercab Production with status=neutral and reality=neutral. Teslarati’s shock-flip line is a five-vehicle authorization margin. Cybercab stayed at 573. The 1,302 figure was not written to robotaxiFleet, cybercab production, or a city row. robotaxiRegistered keeps the later Nov. 14 tracker snapshot of 1,306 (733 Model Y + 573 Cybercab).
- rejected-weak — "Bloomberg says a Tesla-SpaceX merger could be announced in December" (unknown). Fetched https://www.teslarati.com/tesla-spacex-merger-timeline/. It is a Nov. 12 Teslarati rewrite of a Bloomberg people-familiar report: a December announcement is only possible, either side may slip to early 2027, and neither company commented. Terafab is mentioned as existing shared work, not a new site, permit, tool order, or JETI change. No tracked category owns a merger, so it was not refiled under Terafab.

Metric decisions
- Kept robotaxiRegistered 1,306 on 2026-11-14 (733 Model Y + 573 Cybercab). Authorization roster, not cars in service. Cybercab flat versus the Nov. 1 roster of 1,244.
- Kept city sighting floors, basis=sighting-floor, vehicle-mix objects removed so they cannot overwrite the dashboard breakdown (that field is unsupervised / safety-monitor, not Cybercab vs Model Y). The mix remains in the notes. Austin 186 (159 Cybercab + 27 Model Y), Dallas 56, Houston 41, Fort Worth 35, San Antonio 11, Tampa 16. All are 30-day distinct sightings, not dispatch censuses.
- Austin caveat: the prior stored figure cited by the researcher was 405 as of 2026-10-16. This 186 is a different basis (30-day floor). The step-down is not evidence that 219 cars left service. Dallas 56 versus a stored 70 is the same kind of floor, not a company census.
- San Antonio serviceType stays unsupervised only as an inference from other non-Austin Texas cities. Tesla did not say whether a safety monitor is aboard. That limit is in the city note.
- Dropped, and not revived: robotaxiFleet (the 1,306 roster, a 354 sum of city floors, and Electrek’s 666 national figure); Bay Area 6 (stalled community log, not a drop from the stored fleet); Bay Area all-time 771; Austin all-time 509 and VIN-lookup 745; Dallas / Houston / San Antonio VIN-region assignments; Electrek’s 453 Austin figure; Orlando 3 and Miami 0 as too thin or stale; cybercab production count (none); job-postings series (AltIndex 3,943 live and 7,445 October still contradict the last filed point); quarterly production or deliveries (China 8,817 retail, 59,012 exports, and 50 Semis are not an IR quarter); 40 GWh Texas and 18 GWh Berlin (installed or planned, not new measured output); J.P. Morgan’s 400,000 humanoid figure (industry forecast, not Optimus builds).

Curated lint
- python3 scripts/lint_findings.py --curated research/findings/2026-11-14.json --date 2026-11-14
- 0 errors, 0 warnings, 26 keyChanges. No registration-as-fleet, no ownership trespass, no noise URLs in metadata.urlsSeen.

======================================================================
CURATION COMPLETE: 26 validated keyChanges, 4 trends
======================================================================

By category: AI Chip 1, 4680 Battery 2, Cybercab 5, FSD Country Approvals 3, FSD v15 Software 2, Job Postings 4, Optimus 1, Vehicle Production & Delivery 5, Terafab 3.

No sentiment field was rewritten. The only added keyChange is the Texas registry / Waymo item. City-fleet vehicle-mix breakdowns were removed. Cybercab latestStatus now states that the Waymo lead is authorizations and that Cybercab stayed at 573.
