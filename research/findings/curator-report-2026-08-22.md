======================================================================
Tesla Curator - Validation Report
======================================================================

Date: 2026-08-22
Week of: 2026-08-17

[1/4] Category Findings Loaded
✓ 9 categories researched
✓ 17 keyChanges collected

Categories:
  - aiChip: 1 keyChange
  - battery4680: 1 keyChange
  - cybercab: 3 keyChanges
  - fsd: 1 keyChange
  - fsdv15: 2 keyChanges
  - jobPostings: 2 keyChanges
  - optimus: 2 keyChanges
  - productionDelivery: 3 keyChanges
  - terafab: 2 keyChanges

[2/4] Deduplication
✓ Removed 0 duplicates (last week title+category / URL cache / within-week)
✓ Ownership drops (cross-category trespass): 0
✓ Stale-date rejects: 0 (all keyChange dates 2026-08-18 to 2026-08-22)

Kept as genuine new developments (not last-week repeats):
  - Nevada 5,000-vehicle Clark County permit vs last week's 10-vehicle Strip cap
    (same topic, new NTA vote on Aug 20 — explicitly in-scope to keep)
  - jobPostings 5,030 metric vs last week's 5,000 (flat plateau, well-sourced)

JPMorgan Fremont IR note (Teslarati URL) appeared in three categories.
Kept all three under correct owners; differentiated sources so they are
not same-URL duplicates:
  - Cybercab: Teslarati (Model Y holdback)
  - FSD v15: NotATeslaApp #4594 (v15 40% tracks)
  - Optimus: Electrek (H2 2027 sales slip / Fremont SOP)

Glassdoor Tesla jobs URL is in the cache from last week; used only as
the jobPostings metric source, not as a keyChange.

[3/4] Sentiment Validation
✓ 1 sentiment correction applied
  - Nevada NTA 5,000-vehicle permit: status positive → neutral
    (reality already neutral; 7 negative vs 5 positive signals;
     Tesla's own Cybercab lead said they will not fill 5,000 in 12 months,
     first vehicles are Model Y, zero in paid Las Vegas service)

✓ 2 warnings logged (not auto-corrected)
  - Giga Texas cathode video: status=neutral but reality=negative
    (kept: plant-tour non-event, not a new deterioration vs Q2 bottleneck)
  - Semi Europe IAA reveal: status=neutral but reality=negative
    (kept: undated teaser, not a new commercial miss)

Zero remaining status=positive items. That is intentional: this week's
"wins" are paper permits, invite-only events, plant tours, and trade-show
teasers. House style sets status to reality when headlines are inflated.

[4/4] Quality Filter
✓ Rejected 0 weak claims
  (none met Electrek-only+low, <2 signals, or 3+ vague-words+low)

Titles shortened (schema maxLength 120): 0
  (longest title 98 chars)

======================================================================
Category ownership
======================================================================
- Robotaxi fleet/cities/ops (Nevada permit, Sept 3 event, Model Y holdback)
  → Cybercab Production
- FSD OTA / HW3-HW4 ceiling (v15 40% stall, DIY retrofit)
  → FSD v15 Software
- Country certification (Korea origin-split 50M km)
  → FSD Country Approvals
- Optimus SOP / commercial date / competitor units
  → Optimus Production
- AI5/Samsung Taylor foundry, CHIPS, 2nm yields
  → AI Chip Production (not Terafab)
- Terafab land assembly, JETI-era job markdown
  → Terafab In-House Chip Manufacturing
- Semi orders / IAA / Model Y L US production
  → Vehicle Production & Delivery
- Hiring mix (Optimus mocap/sim, FSD supervisors)
  → Job Postings

Las Vegas fleetUpdate (mapped, vehicleCount=0) was NOT written as a
global robotaxiFleet metric point.

======================================================================
Accepted keyChanges (17)
======================================================================
 1. [neutral ] Cybercab Production: Nevada NTA replaces 10-vehicle cap with 5,000-robotaxi Clark County permit
 2. [neutral ] Cybercab Production: Tesla sets Sept 3 Austin Cybercab launch event — paid public service still unconfirmed
 3. [negative] Cybercab Production: Tesla tells JPMorgan it is holding back Model Y robotaxis to wait for Cybercab
 4. [negative] Optimus Production: Tesla IR tells JPMorgan Optimus sales slip to H2 2027; Fremont SOP still unconfirmed
 5. [negative] FSD v15 Software: IR restates FSD v15 as a step-change; still ~40% of tracks after 4 weeks, consumer on v14
 6. [negative] Optimus Production: Unitree IPO hits $66B after selling 5,215 humanoids; Tesla Optimus still pre-revenue
 7. [neutral ] Vehicle Production & Delivery: Einride orders 500 Tesla Semis — largest Semi deal, still a rounding error vs auto volume
 8. [negative] FSD Country Approvals: Korea FSD remains origin-split: Shanghai-built majority fleet still blocked despite 50M km
 9. [neutral ] 4680 Battery Cell Production: Giga Texas cathode video is a 10 GWh Early Ramp tour, not a 4680 GWh win
10. [negative] FSD v15 Software: DIY HW3-to-HW4 retrofit shows swap is feasible; Tesla still has no official program
11. [negative] Job Postings: Optimus hiring this week is mocap, training, and simulation — not a production-line ramp
12. [neutral ] Job Postings: FSD hiring pulse is a U.S. data-collection supervisor wave, not a core Autopilot engineering surge
13. [neutral ] Vehicle Production & Delivery: Model Y L appears in Giga Texas outbound lots — US production live, deliveries still October
14. [negative] AI Chip Production: Samsung Taylor Fab 1 still dark; Tesla AI5 first product in 2027, CHIPS funds unpaid
15. [neutral ] Terafab In-House Chip Manufacturing: WIT TECH land holdings jump to 4,620 acres — still ~21% of advertised 22,000-acre site
16. [neutral ] Vehicle Production & Delivery: Tesla confirms Semi Europe reveal at IAA — still no on-sale date, 9 years after 2017 unveil
17. [negative] Terafab In-House Chip Manufacturing: Chamber briefing cites 1,500 Terafab jobs vs SpaceX's 3,000 pledge; 9–10 year build

Status mix: 0 positive / 9 negative / 8 neutral

======================================================================
Metrics Merged
======================================================================
- cybercab: []  (no new VIN/production count; last point remains VIN #2172)
- robotaxiFleet: []  (no verified global in-service count; LV 0 is mapped-city
  status, not a global fleet print of 0)
- jobPostings: 1 point
    date=2026-08-22 count=5030
    note: Glassdoor ~5,030 / Indeed ~5,020; flat vs Aug 15 ~5,000 plateau
- quarterlyData: []  (no official Q3 P&D print)
- categoryUpdates: aiChip, battery4680, cybercab, fsd, fsdv15, jobPostings,
  optimus, productionDelivery, terafab
- urlsSeen: 25 (canonical keyChange articles + ≤2 corroborators; LinkedIn
  job URLs, Glassdoor/Indeed homepages, tesla.com/careers stripped)

Trends: 5 (robotaxi paper-permit vs service; Optimus H2 2027 slip vs Unitree
shipping; FSD software+country dual stall; auto volume miss dressed with
Semi PR; Taylor/Terafab still years from wafers)

======================================================================
✓ CURATION COMPLETE: 17 validated keyChanges
  Output: /Users/gonzalosolis/Research/research/findings/2026-08-22.json
  Report: research/findings/curator-report-2026-08-22.md
======================================================================
