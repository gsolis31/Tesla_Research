#!/usr/bin/env python3
"""
Tesla Curator - Data Quality Validation
Deduplicates, validates sentiment, rejects weak claims, and normalizes data
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Category name normalization
CATEGORY_NAMES = {
    'aichip': 'AI Chip Production',
    'ai chip production': 'AI Chip Production',
    'ai chip manufacturing partnership': 'AI Chip Production',
    'ai chip manufacturing': 'AI Chip Production',
    'ai chip development process': 'AI Chip Production',
    'ai chip manufacturing strategy': 'AI Chip Production',
    'ai infrastructure & strategy': 'AI Chip Production',
    'battery4680': '4680 Battery Cell Production',
    '4680 production capacity': '4680 Battery Cell Production',
    '4680 manufacturing technology': '4680 Battery Cell Production',
    '4680 technology development': '4680 Battery Cell Production',
    '4680 production & cost': '4680 Battery Cell Production',
    '4680 production milestone': '4680 Battery Cell Production',
    'cybercab': 'Cybercab Production',
    'cybercab production': 'Cybercab Production',
    'fsd': 'FSD Country Approvals',
    'fsd country approvals': 'FSD Country Approvals',
    'fsd safety & regulation': 'FSD Country Approvals',
    'fsd v14 software': 'FSD v14 Software',
    'optimus': 'Optimus Production',
    'optimus production': 'Optimus Production',
    'optimus job postings': 'Job Postings',
    'optimus hiring velocity': 'Job Postings',
    'productiondelivery': 'Vehicle Production & Delivery',
    'vehicle production & delivery': 'Vehicle Production & Delivery',
    'terafab': 'Terafab Manufacturing',
    'terafab announcement': 'Terafab Manufacturing',
    'terafab chip production': 'Terafab Manufacturing',
    'terafab execution risk': 'Terafab Manufacturing',
    'terafab north campus': 'Terafab Manufacturing',
    'jobpostings': 'Job Postings',
    'job postings': 'Job Postings',
    'fsdv15': 'FSD v15 Software',
    'fsd v15 software': 'FSD v15 Software'
}

VAGUE_WORDS = ['possible', 'maybe', 'could', 'might', 'potentially', 'reportedly', 'appears', 'suggests']

def load_config():
    """Load curator configuration"""
    config_path = Path('/Users/gonzalosolis/Research/research/configs/curator-config.json')
    with open(config_path) as f:
        return json.load(f)

def load_category_findings(config: Dict) -> List[Dict]:
    """Load all category findings files"""
    findings = []
    for file_path in config['findingsFiles']:
        full_path = Path('/Users/gonzalosolis/Research') / file_path
        if full_path.exists():
            with open(full_path) as f:
                data = json.load(f)
                findings.append(data)
        else:
            print(f"⚠️  Warning: {file_path} not found")
    return findings

def collect_key_changes(category_findings: List[Dict]) -> List[Dict]:
    """Collect all keyChanges from category findings"""
    all_key_changes = []
    for category_data in category_findings:
        for kc in category_data.get('keyChanges', []):
            kc['_sourceCategory'] = category_data.get('categoryKey', 'unknown')
            all_key_changes.append(kc)
    return all_key_changes

def load_url_cache(url_cache_path: str) -> Dict:
    """Load URL cache"""
    cache_path = Path(url_cache_path)
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    return {'urls': {}}

def deduplicate_key_changes(all_key_changes: List[Dict], last_week_kcs: List[Dict], url_cache: Dict) -> tuple:
    """
    Deduplicate keyChanges against:
    1. Last week's keyChanges (same title + category)
    2. URL cache (URL already seen)
    3. Within this week (same title + category)
    """
    seen_titles = set()
    deduplicated = []
    duplicate_count = 0

    for kc in all_key_changes:
        title = kc.get('title', '').strip()
        category = kc.get('category', '').strip()
        source_url = kc.get('source', '')

        is_dup = False

        # Check against last week
        for last_kc in last_week_kcs:
            if (last_kc.get('title', '').strip() == title and
                last_kc.get('category', '').strip() == category):
                is_dup = True
                break

        # Check URL cache
        if not is_dup and source_url and source_url in url_cache.get('urls', {}):
            is_dup = True

        # Check within this week
        key = f"{category}|{title}"
        if not is_dup and key in seen_titles:
            is_dup = True

        if is_dup:
            duplicate_count += 1
        else:
            seen_titles.add(key)
            deduplicated.append(kc)

    return deduplicated, duplicate_count

def validate_sentiment(key_changes: List[Dict]) -> int:
    """
    Validate sentiment and auto-correct ERROR-level issues.
    Returns count of corrections made.
    """
    corrected_count = 0

    for kc in key_changes:
        status = kc.get('status')
        sentiment = kc.get('sentiment', {})
        reality = sentiment.get('reality')
        evidence = kc.get('evidence', {})

        # Critical: status must match reality
        if status == 'positive' and reality == 'negative':
            kc['status'] = 'negative'
            corrected_count += 1
            print(f"✓ Auto-corrected: {kc['title']} → status now negative")

        # Check evidence balance (warn only)
        pos_count = len(evidence.get('positive_signals', []))
        neg_count = len(evidence.get('negative_signals', []))

        if neg_count > pos_count and status == 'positive':
            print(f"⚠️  Warning: {kc['title']} has more negative signals but positive status")

    return corrected_count

def filter_weak_claims(key_changes: List[Dict]) -> tuple:
    """
    Filter out weak claims based on:
    1. Electrek-only source + low confidence
    2. Insufficient evidence (< 2 signals total)
    3. Too vague (3+ vague words + low confidence)
    """
    filtered = []
    rejected = []

    for kc in key_changes:
        source = kc.get('source', '')
        sentiment = kc.get('sentiment', {})
        confidence = sentiment.get('confidence', 'medium')
        evidence = kc.get('evidence', {})
        description = kc.get('description', '').lower()

        is_weak = False
        reason = None

        # Electrek-only + low confidence
        if 'electrek.co' in source and confidence == 'low':
            is_weak = True
            reason = "electrek_only_low_confidence"

        # Insufficient evidence
        total_signals = len(evidence.get('positive_signals', [])) + len(evidence.get('negative_signals', []))
        if total_signals < 2:
            is_weak = True
            reason = "insufficient_evidence"

        # Too vague
        vague_count = sum(1 for word in VAGUE_WORDS if word in description)
        if vague_count >= 3 and confidence == 'low':
            is_weak = True
            reason = "too_vague"

        if is_weak:
            rejected.append({'title': kc['title'], 'reason': reason})
        else:
            filtered.append(kc)

    return filtered, rejected

def normalize_key_changes(key_changes: List[Dict]):
    """Normalize category names, status, and confidence"""
    for kc in key_changes:
        # Normalize category
        category = kc.get('category', '').lower().strip()
        normalized = CATEGORY_NAMES.get(category, kc.get('category', 'Unknown'))
        kc['category'] = normalized

        # Validate status
        if kc.get('status') not in ['positive', 'negative', 'neutral']:
            kc['status'] = 'neutral'

        # Validate confidence
        if 'sentiment' in kc:
            confidence = kc['sentiment'].get('confidence', 'medium')
            if confidence not in ['high', 'medium', 'low']:
                kc['sentiment']['confidence'] = 'medium'

def extract_trends(key_changes: List[Dict]) -> List[str]:
    """Extract trends from keyChanges by category"""
    trends = []
    by_category = defaultdict(list)

    for kc in key_changes:
        category = kc.get('category', 'Unknown')
        by_category[category].append(kc)

    for category, kcs in by_category.items():
        if len(kcs) == 1:
            trends.append(f"{category}: {kcs[0]['title']}")
        else:
            pos = sum(1 for kc in kcs if kc['status'] == 'positive')
            neg = sum(1 for kc in kcs if kc['status'] == 'negative')

            if neg > pos:
                trends.append(f"{category}: Mixed signals with concerning developments")
            elif pos > neg:
                trends.append(f"{category}: Progress across multiple fronts")
            else:
                trends.append(f"{category}: Balanced developments")

    return trends[:4]

def merge_metrics_and_updates(category_findings: List[Dict]) -> tuple:
    """Merge metrics, quarterly data, and category updates"""
    metrics = {'cybercab': [], 'robotaxiFleet': [], 'jobPostings': []}
    quarterly_data = []
    category_updates = {}

    for category_data in category_findings:
        category_key = category_data.get('categoryKey')

        # Metric updates
        if category_data.get('metricUpdate'):
            if category_key == 'cybercab':
                metrics['cybercab'].append(category_data['metricUpdate'])
            elif category_key == 'jobPostings':
                metrics['jobPostings'].append(category_data['metricUpdate'])
            elif category_key == 'battery4680':
                if 'battery4680' not in metrics:
                    metrics['battery4680'] = []
                metrics['battery4680'].append(category_data['metricUpdate'])

        # Fleet updates
        if category_data.get('fleetUpdate'):
            metrics['robotaxiFleet'].append(category_data['fleetUpdate'])

        # Quarterly data
        if category_key == 'productionDelivery' and category_data.get('metricUpdate', {}).get('quarterlyData'):
            quarterly_data.append(category_data['metricUpdate']['quarterlyData'])

        # Category updates
        if category_data.get('categoryUpdate'):
            category_updates[category_key] = category_data['categoryUpdate']

    return metrics, quarterly_data, category_updates

def write_final_findings(config: Dict, filtered: List[Dict], trends: List[str],
                         metrics: Dict, quarterly_data: List, category_updates: Dict,
                         category_findings: List[Dict], all_key_changes: List[Dict],
                         duplicate_count: int, corrected_count: int, rejected: List[Dict]):
    """Write final findings to JSON file"""
    date = config['date']
    week_of = config['weekOf']

    # Collect all URLs seen
    all_urls_seen = set()
    all_sources_searched = set()
    categories_researched = []

    for cf in category_findings:
        all_urls_seen.update(cf.get('urlsSeen', []))
        all_sources_searched.update(cf.get('metadata', {}).get('sourcesSearched', []))
        if cf.get('categoryKey'):
            categories_researched.append(cf['categoryKey'])

    # Check if we have any news
    has_news = len(filtered) > 0 or any(len(v) > 0 for v in metrics.values()) or len(quarterly_data) > 0

    if not has_news:
        final_findings = {
            'date': date,
            'weekOf': week_of,
            'findings': {'keyChanges': [], 'trends': []},
            'metadata': {
                'skipReason': 'No significant news found across all categories',
                'categoriesResearched': categories_researched
            }
        }
    else:
        final_findings = {
            'date': date,
            'weekOf': week_of,
            'findings': {
                'keyChanges': filtered,
                'trends': trends,
                'metrics': metrics,
                'quarterlyData': quarterly_data,
                'categoryUpdates': category_updates
            },
            'metadata': {
                'sourcesSearched': sorted(list(all_sources_searched)),
                'urlsSeen': sorted(list(all_urls_seen)),
                'categoriesResearched': categories_researched,
                'validationSummary': {
                    'totalKeyChanges': len(all_key_changes),
                    'duplicatesRemoved': duplicate_count,
                    'sentimentCorrected': corrected_count,
                    'weakClaimsRejected': len(rejected),
                    'rejectedClaims': rejected
                }
            }
        }

    # Write output
    output_path = Path('/Users/gonzalosolis/Research/research/findings') / f'{date}.json'
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(final_findings, f, indent=2)

    return output_path, has_news

def generate_validation_report(config: Dict, category_findings: List[Dict],
                                all_key_changes: List[Dict], deduplicated: List[Dict],
                                filtered: List[Dict], corrected_count: int,
                                rejected: List[Dict], trends: List[str]) -> str:
    """Generate validation report"""
    date = config['date']
    week_of = config['weekOf']
    duplicate_count = len(all_key_changes) - len(deduplicated)

    report = f"""
======================================================================
Tesla Curator - Validation Report
======================================================================

Date: {date}
Week of: {week_of}

[1/4] Category Findings Loaded
✓ {len(category_findings)} categories researched
✓ {len(all_key_changes)} keyChanges collected

[2/4] Deduplication
✓ Removed {duplicate_count} duplicates

[3/4] Sentiment Validation
✓ {corrected_count} sentiment corrections applied

[4/4] Quality Filter
✓ Rejected {len(rejected)} weak claims

Rejected Claims:
"""
    for reject in rejected:
        report += f"  - {reject['title']} (reason: {reject['reason']})\n"

    report += f"""
======================================================================
✓ CURATION COMPLETE: {len(filtered)} validated keyChanges
======================================================================

Trends Extracted:
"""
    for trend in trends:
        report += f"  - {trend}\n"

    return report

def main():
    print("======================================================================")
    print("Tesla Curator - Starting Data Quality Validation")
    print("======================================================================\n")

    # Step 1: Load configuration
    print("[1/9] Loading configuration...")
    config = load_config()
    print(f"✓ Date: {config['date']}, Week of: {config['weekOf']}")

    # Step 2: Load category findings
    print("\n[2/9] Loading category findings...")
    category_findings = load_category_findings(config)
    print(f"✓ Loaded {len(category_findings)} category findings")

    # Step 3: Collect key changes
    print("\n[3/9] Collecting keyChanges...")
    all_key_changes = collect_key_changes(category_findings)
    print(f"✓ Collected {len(all_key_changes)} keyChanges")

    # Step 4: Deduplicate
    print("\n[4/9] Deduplicating...")
    last_week_kcs = config['hotContext']['lastWeekKeyChanges']
    url_cache = load_url_cache(config['hotContext']['urlCache'])
    deduplicated, duplicate_count = deduplicate_key_changes(all_key_changes, last_week_kcs, url_cache)
    print(f"✓ Removed {duplicate_count} duplicates")
    print(f"✓ Remaining: {len(deduplicated)} keyChanges")

    # Step 5: Validate sentiment
    print("\n[5/9] Validating sentiment...")
    corrected_count = validate_sentiment(deduplicated)
    print(f"✓ Applied {corrected_count} sentiment corrections")

    # Step 6: Filter weak claims
    print("\n[6/9] Filtering weak claims...")
    filtered, rejected = filter_weak_claims(deduplicated)
    print(f"✓ Rejected {len(rejected)} weak claims")
    print(f"✓ Remaining: {len(filtered)} keyChanges")

    # Step 7: Normalize data
    print("\n[7/9] Normalizing data...")
    normalize_key_changes(filtered)
    print(f"✓ Normalized {len(filtered)} keyChanges")

    # Step 8: Extract trends
    print("\n[8/9] Extracting trends...")
    trends = extract_trends(filtered)
    print(f"✓ Extracted {len(trends)} trends")

    # Step 9: Merge metrics and write output
    print("\n[9/9] Merging metrics and writing output...")
    metrics, quarterly_data, category_updates = merge_metrics_and_updates(category_findings)
    output_path, has_news = write_final_findings(
        config, filtered, trends, metrics, quarterly_data, category_updates,
        category_findings, all_key_changes, duplicate_count, corrected_count, rejected
    )
    print(f"✓ Written {output_path}")

    # Generate validation report
    report = generate_validation_report(
        config, category_findings, all_key_changes, deduplicated,
        filtered, corrected_count, rejected, trends
    )

    report_path = Path('/Users/gonzalosolis/Research/research/findings') / f'curator-report-{config["date"]}.md'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Written {report_path}")

    print("\n" + report)

    if not has_news:
        print("\n⚠️  NO SIGNIFICANT NEWS FOUND")
    else:
        print(f"\n✓ CURATION COMPLETE: {len(filtered)} validated keyChanges")

if __name__ == '__main__':
    main()
