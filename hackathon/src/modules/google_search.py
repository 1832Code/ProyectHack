"""
Google Search Module
Author: Mauricio J. @synaw_w
"""

from typing import List, Optional, Dict, Any
import os
import logging
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from apify_client import ApifyClient

logger = logging.getLogger(__name__)

_google_cache_dir = Path("/tmp/google_cache")
_cache_max_size = 50
_cache_ttl_hours = 24

try:
    _google_cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Google cache directory initialized: {_google_cache_dir}")
except Exception as e:
    logger.error(f"❌ Failed to create Google cache directory: {e}", exc_info=True)


def _get_google_cache_key(query: str, country_code: Optional[str], language_code: Optional[str], max_items: int, results_per_page: int) -> str:
    """Generate a cache key for Google results."""
    key_parts = [
        query.lower().strip(),
        country_code or "",
        language_code or "",
        str(max_items),
        str(results_per_page)
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _get_google_cache_file_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return _google_cache_dir / f"{cache_key}.json"


def _load_google_cache(cache_key: str) -> Optional[List[Dict[str, Any]]]:
    """Load Google results from cache."""
    cache_file = _get_google_cache_file_path(cache_key)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        cached_time_str = cache_data.get('timestamp', '')
        if not cached_time_str:
            cache_file.unlink()
            return None
        
        cached_time = datetime.fromisoformat(cached_time_str)
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=_cache_ttl_hours):
            logger.info(f"Google cache entry expired (age: {age.total_seconds()/3600:.1f}h)")
            cache_file.unlink()
            return None
        
        results = cache_data.get('results', [])
        logger.info(f"✅✅✅ GOOGLE CACHE HIT - Using cached results (NO APIFY API CALLS - SAVING CREDITS)")
        logger.info(f"   Cache age: {age.total_seconds()/60:.1f} minutes")
        return results
    except Exception as e:
        logger.warning(f"Error loading Google cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_google_cache(cache_key: str, results: List[Dict[str, Any]]) -> None:
    """Save Google results to cache."""
    try:
        cache_file = _get_google_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved Google cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        _cleanup_old_google_cache()
    except Exception as e:
        logger.error(f"Error saving Google cache: {e}", exc_info=True)


def _cleanup_old_google_cache() -> None:
    """Remove old cache files if cache directory is too large."""
    try:
        cache_files = sorted(
            _google_cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if len(cache_files) > _cache_max_size:
            for file_to_remove in cache_files[_cache_max_size:]:
                try:
                    file_to_remove.unlink()
                    logger.info(f"Cleaned up old Google cache file: {file_to_remove.name}")
                except Exception as e:
                    logger.warning(f"Error removing cache file {file_to_remove.name}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning up Google cache: {e}")


def search_google(
    client: ApifyClient,
    query: str,
    max_items: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    results_per_page: int = 10,
    use_cache: bool = True,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Google using Apify actor apify/google-search-scraper.
    
    Args:
        client: Apify client instance
        query: Search query
        max_items: Maximum number of results
        country_code: Optional country code
        language_code: Optional language code
        results_per_page: Results per page (10, 20, 30, 40, 50, 100)
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        List of search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_google_cache_key(query, country_code, language_code, max_items, results_per_page)
        cached_results = _load_google_cache(cache_key)
        
        if cached_results:
            logger.info(f"✅✅✅ Using cached Google results - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ Google cache MISS - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   Google cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring Google cache")
    
    try:
        logger.info(f"Starting Google search for: {query}")
        
        run_input = {
            "focusOnPaidAds": False,
            "forceExactMatch": False,
            "includeIcons": False,
            "includeUnfilteredResults": False,
            "maxPagesPerQuery": 1,
            "maximumLeadsEnrichmentRecords": 0,
            "mobileResults": False,
            "queries": query,
            "resultsPerPage": min(results_per_page, 100),
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
        results = list(dataset.items)
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        results = results[:max_items]
        
        if use_cache:
            cache_key = _get_google_cache_key(query, country_code, language_code, max_items, results_per_page)
            _save_google_cache(cache_key, results)
            logger.info(f"✅ Cached Google results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in Google search: {e}", exc_info=True)
        raise

