======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-07-23
Week of: 2026-07-20

[1/4] Category Findings Loaded
✓ 9 categories researched
✓ 18 keyChanges collected

Categories:
  - aiChip: 2 keyChanges
  - battery4680: 1 keyChanges
  - cybercab: 3 keyChanges
  - fsd: 2 keyChanges
  - fsdv15: 3 keyChanges
  - jobPostings: 1 keyChanges
  - optimus: 2 keyChanges
  - productionDelivery: 2 keyChanges
  - terafab: 2 keyChanges

[2/4] Deduplication
✓ Removed 0 duplicates (last week + URL cache + within-week)
✓ Ownership drops (cross-category trespass only): 0
  (none)


[3/4] Sentiment Validation
✓ 0 sentiment corrections applied (status=positive + reality=negative → status=negative)
✓ 1 warnings logged
  - status=positive but reality=neutral: Q2 IR: 1.48M paid FSD customers (+200k QoQ, +56% YoY); 55% North America delivery attach —

[4/4] Quality Filter
✓ Rejected 0 weak claims
  (none)

Titles shortened (schema maxLength 120): 3
  - Q2 IR: battery pack capacity is the global vehicle bottleneck; 4680 ramp for Cybercab/Semi/MY
  - Q2 IR: 1.48M paid FSD customers (+200k QoQ, +56% YoY); 55% North America delivery attach
  - Q2 earnings: Musk confirms Optimus has no supply chain and a 'flat and long' ramp

======================================================================
Metrics Merged
======================================================================
- cybercab metricUpdates: 1
  {
  "date": "2026-07-22",
  "count": 125000,
  "note": "Q2 2026 materials cite Cybercab installed annual production capacity exceeding 125,000 units at Giga Texas after production start. This is line capacity, not verified commercial output or fleet deployment. Paid robotaxi service remains Model Y\...
- robotaxiFleet updates: 1
  city=Orlando
- jobPostings metricUpdates: 0
- categoryUpdates: aiChip, battery4680, cybercab, fsd, fsdv15, jobPostings, optimus, productionDelivery, terafab
- urlsSeen: 17 (canonical keyChange sources + ≤2 corroborators)

======================================================================
Accepted keyChanges (18)
======================================================================
 1. [neutral] AI Chip Production: Q2 Call: AI5 Volume Still 'Hopefully 2027'; Samsung/TSMC/Micron Named; AI6 Boast Unbacked
 2. [neutral] AI Chip Production: Micron Multi-Year Memory Allocation Highlighted; AI Board BOM Still Supply-Risk Bound
 3. [negative] 4680 Battery Cell Production: Q2 IR: battery pack capacity is the global vehicle bottleneck; 4680 ramp for Cybercab/Semi/MY
 4. [neutral] Cybercab Production: Tesla adds unsupervised Robotaxi in Orlando and Tampa — 7 metros, still tiny fleets
 5. [neutral] Cybercab Production: Cybercab: Giga Texas production + 125k capacity claim; Moravy says no more federal approvals needed
 6. [negative] Cybercab Production: Q2 Robotaxi data: 2.4M paid miles but QoQ flat; Musk blames safety, fleet still not scaling
 7. [negative] FSD Country Approvals: NHTSA EA26002 escalates: demands Tesla 'Radar Saves Us' internal docs and marketing justification
 8. [negative] FSD Country Approvals: France rejects FSD Supervised: Transport Minister cites speeding and driver-monitoring gaps
 9. [neutral] FSD v15 Software: FSD v14 Lite goes public for HW3 (2026.20.6.10/.11); HW4 gets point-release v14.3.6 — still Supervised only
10. [neutral] FSD v15 Software: Ashok: Robotaxi fleet already running early FSD v15 builds — only ~40% of planned improvements, consumer still on v14
11. [positive] FSD v15 Software: Q2 IR: 1.48M paid FSD customers (+200k QoQ, +56% YoY); 55% North America delivery attach
12. [neutral] Job Postings: Optimus hiring pulse continues — manufacturing/test/production roles, but still no fill-rate or headcount proof
13. [negative] Optimus Production: Q2 earnings: Musk confirms Optimus has no supply chain and a 'flat and long' ramp
14. [neutral] Optimus Production: Tesla app quietly builds Optimus phone-key and in-home data consent — software shell years ahead of product
15. [negative] Vehicle Production & Delivery: Q2 earnings: record $28.2B revenue, but op margin collapses to 1.4% and FCF goes negative
16. [negative] Vehicle Production & Delivery: TSLA drops ~14.5% post-earnings as Street digests profit miss and $25B+ CapEx path
17. [neutral] Terafab Manufacturing: Gov. Abbott Submits Positive JETI Determinations for SpaceX Terafab; Deal Still Needs Formal Signing
18. [neutral] Terafab Manufacturing: Tesla Q2 Update: Early-Stage Austin Semiconductor Fab Construction and Equipment Procurement Underway

Trends:
  - Cybercab Production: Mixed signals with concerning developments
  - FSD v15 Software: Progress across multiple fronts
  - FSD Country Approvals: Mixed signals with concerning developments
  - Vehicle Production & Delivery: Mixed signals with concerning developments

======================================================================
✓ CURATION COMPLETE: 18 validated keyChanges
  Output: /Users/gonzalosolis/Research/research/findings/2026-07-23.json
  Report: research/findings/curator-report-2026-07-23.md
======================================================================

======================================================================
Metric Curation Notes
======================================================================
- REJECTED cybercab metricUpdate count=125000 (installed annual *capacity*, not
  vehicle unit count). Would break cybercab production time series (last point
  was ~120 staging-lot units). Capacity claim retained in keyChange only.
- NORMALIZED robotaxiFleet city-shaped fleetUpdate → active-fleet point
  count=21 on 2026-07-22 (Electrek ~21 estimate; prior point was 20 on 2026-07-08).
  Raw fleetUpdate had vehicleCount=null which merge would coerce to 0.

