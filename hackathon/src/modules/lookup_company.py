"""
Module for company lookup functionality using Apify
Author: Mauricio J. @synaw_w
"""

import os
import logging
from typing import Dict, Any, List, Optional
from apify_client import ApifyClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


def get_apify_client() -> ApifyClient:
    """
    Get Apify client instance using API token from environment.
    
    Returns:
        ApifyClient: Configured Apify client instance
        
    Raises:
        ValueError: If APIFY_API_TOKEN is not set
    """
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        raise ValueError("APIFY_API_TOKEN environment variable is not set")
    
    return ApifyClient(api_token)


def lookup_company(
    client: ApifyClient,
    company: str,
    keywords: Optional[List[str]] = None,
    max_items_per_query: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Lookup company information and related keywords using Apify.
    
    Args:
        client: Apify client instance
        company: Company name to search
        keywords: Optional list of related keywords
        max_items_per_query: Maximum items per search query
        country_code: Optional country code filter
        language_code: Optional language code filter
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        Dict containing search results for company and keywords
    """
    results = {
        "company": company,
        "keywords": keywords or [],
        "company_results": [],
        "keyword_results": {}
    }
    
    try:
        logger.info(f"Starting company lookup for: {company}")
        
        run_input = {
            "focusOnPaidAds": False,
            "forceExactMatch": False,
            "includeIcons": False,
            "includeUnfilteredResults": False,
            "maxPagesPerQuery": 1,
            "maximumLeadsEnrichmentRecords": 0,
            "mobileResults": False,
            "queries": company,
            "resultsPerPage": min(max_items_per_query, 100),
            "saveHtml": False,
            "saveHtmlToKeyValueStore": True,
            "aiMode": "aiModeOff",
            "searchLanguage": language_code or "",
            "languageCode": language_code or "",
            "wordsInTitle": [],
            "wordsInText": [],
            "wordsInUrl": []
        }
        
        run = client.actor("apify/google-search-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results["company_results"] = list(dataset.items)
        
        logger.info(f"Found {len(results['company_results'])} results for company: {company}")
        
        if keywords:
            results["keyword_results"] = {}
            for keyword in keywords:
                try:
                    keyword_input = {
                        "focusOnPaidAds": False,
                        "forceExactMatch": False,
                        "includeIcons": False,
                        "includeUnfilteredResults": False,
                        "maxPagesPerQuery": 1,
                        "maximumLeadsEnrichmentRecords": 0,
                        "mobileResults": False,
                        "queries": keyword,
                        "resultsPerPage": min(max_items_per_query, 100),
                        "saveHtml": False,
                        "saveHtmlToKeyValueStore": True,
                        "aiMode": "aiModeOff",
                        "searchLanguage": language_code or "",
                        "languageCode": language_code or "",
                        "wordsInTitle": [],
                        "wordsInText": [],
                        "wordsInUrl": []
                    }
                    
                    keyword_run = client.actor("apify/google-search-scraper").call(run_input=keyword_input)
                    keyword_dataset = client.dataset(keyword_run["defaultDatasetId"]).list_items()
                    results["keyword_results"][keyword] = list(keyword_dataset.items)
                    
                    logger.info(f"Found {len(results['keyword_results'][keyword])} results for keyword: {keyword}")
                except Exception as e:
                    logger.error(f"Error searching keyword '{keyword}': {e}")
                    results["keyword_results"][keyword] = []
        
    except Exception as e:
        logger.error(f"Error in company lookup: {e}")
        raise
    
    return results


def get_summary_stats(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate summary statistics from lookup results.
    
    Args:
        results: Results dictionary from lookup_company
        
    Returns:
        Dict containing summary statistics
    """
    company_results = results.get("company_results", [])
    keyword_results = results.get("keyword_results", {})
    
    total_company_results = len(company_results)
    total_keyword_results = sum(len(items) for items in keyword_results.values())
    
    stats = {
        "total_company_results": total_company_results,
        "total_keyword_results": total_keyword_results,
        "total_results": total_company_results + total_keyword_results,
        "keywords_searched": len(keyword_results),
        "keywords_with_results": sum(1 for items in keyword_results.values() if len(items) > 0)
    }
    
    return stats

