"""
Web search functionality for Tesla tracker
Uses Serper API for Google search results
"""

import os
import requests

def search_google(query, num_results=10):
    """
    Search Google using Serper API

    Args:
        query: Search query string
        num_results: Number of results to return (default 10)

    Returns:
        List of search results with titles, links, and snippets
    """
    api_key = os.environ.get('SERPER_API_KEY')
    if not api_key:
        print("WARNING: SERPER_API_KEY not found. Using fallback mode.")
        return []

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": num_results
    }

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        results = []
        if 'organic' in data:
            for item in data['organic'][:num_results]:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'date': item.get('date', '')
                })

        return results

    except Exception as e:
        print(f"Search error: {str(e)}")
        return []


def search_tesla_news(category, start_date, end_date):
    """
    Search for Tesla news in a specific category

    Args:
        category: News category (e.g., "Cybercab", "FSD", etc.)
        start_date: Start date for search (YYYY-MM-DD)
        end_date: End date for search (YYYY-MM-DD)

    Returns:
        List of relevant search results
    """
    # Category-specific search queries
    queries = {
        "Cybercab": "Tesla robotaxi cybercab production fleet",
        "FSD": "Tesla FSD approval country regulatory",
        "AI Chip": "Tesla AI5 AI6 chip Samsung TSMC production",
        "Optimus": "Tesla Optimus robot production timeline",
        "Job Postings": "Tesla Optimus job postings hiring"
    }

    query = queries.get(category, f"Tesla {category}")

    # Add date range and news sources
    query += f" after:{start_date} before:{end_date}"
    query += " site:electrek.co OR site:teslarati.com OR site:teslanorth.com OR site:basenor.com"

    return search_google(query, num_results=5)
