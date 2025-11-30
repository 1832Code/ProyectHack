"""
X (Twitter) Search Module
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_x_cache_dir = Path("/tmp/x_cache")
_cache_max_size = 50
_cache_ttl_hours = 24

try:
    _x_cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ X cache directory initialized: {_x_cache_dir}")
except Exception as e:
    logger.error(f"❌ Failed to create X cache directory: {e}", exc_info=True)


def _get_x_cache_key(query: str, geocode: Optional[str], max_items: int, sort: str, tweet_language: str) -> str:
    """Generate a cache key for X results."""
    key_parts = [
        query.lower().strip(),
        geocode or "",
        str(max_items),
        sort,
        tweet_language
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _get_x_cache_file_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return _x_cache_dir / f"{cache_key}.json"


def _load_x_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Load X results from cache."""
    cache_file = _get_x_cache_file_path(cache_key)
    
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
            logger.info(f"X cache entry expired (age: {age.total_seconds()/3600:.1f}h)")
            cache_file.unlink()
            return None
        
        results = cache_data.get('results', {})
        logger.info(f"✅✅✅ X CACHE HIT - Using cached results (NO APIFY API CALLS - SAVING CREDITS)")
        logger.info(f"   Cache age: {age.total_seconds()/60:.1f} minutes")
        return results
    except Exception as e:
        logger.warning(f"Error loading X cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_x_cache(cache_key: str, results: Dict[str, Any]) -> None:
    """Save X results to cache."""
    try:
        cache_file = _get_x_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved X cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        _cleanup_old_x_cache()
    except Exception as e:
        logger.error(f"Error saving X cache: {e}", exc_info=True)


def _cleanup_old_x_cache() -> None:
    """Remove old cache files if cache directory is too large."""
    try:
        cache_files = sorted(
            _x_cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if len(cache_files) > _cache_max_size:
            for file_to_remove in cache_files[_cache_max_size:]:
                try:
                    file_to_remove.unlink()
                    logger.info(f"Cleaned up old X cache file: {file_to_remove.name}")
                except Exception as e:
                    logger.warning(f"Error removing cache file {file_to_remove.name}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning up X cache: {e}")


def search_x(
    client: ApifyClient,
    query: str,
    max_items: int = 1000,
    geocode: Optional[str] = None,
    sort: str = "Latest",
    tweet_language: str = "es",
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Search X (Twitter) content using Apify actor apidojo/twitter-scraper-lite.
    
    Args:
        client: Apify client instance
        query: Search query
        max_items: Maximum number of results (default: 1000)
        geocode: Optional geocode in format "latitude,longitude,radius" (e.g., "-12.0257733,-77.3174516,20km")
        sort: Sort order - "Latest", "Top", "People", "Photos", "Videos" (default: "Latest")
        tweet_language: Language code for tweets (default: "es")
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        Dict containing search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_x_cache_key(query, geocode, max_items, sort, tweet_language)
        logger.info(f"🔍 Looking for X cache with key: {cache_key[:16]}... (query: '{query}', max_items: {max_items})")
        cached_results = _load_x_cache(cache_key)
        
        if cached_results:
            cached_results_list = cached_results.get("results", [])
            logger.info(f"📦 Cache found with {len(cached_results_list)} items, requested: {max_items}")
            if len(cached_results_list) > max_items:
                logger.info(f"✅✅✅ Using cached X results - limiting from {len(cached_results_list)} to {max_items} - NO APIFY API CALLS")
                cached_results["results"] = cached_results_list[:max_items]
            else:
                logger.info(f"✅✅✅ Using cached X results ({len(cached_results_list)} items) - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ X cache MISS for max_items={max_items} - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   X cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring X cache")
    
    results = {
        "query": query,
        "geocode": geocode,
        "results": []
    }
    
    try:
        logger.info(f"Starting X search for: {query} (max_items: {max_items}, geocode: {geocode}, sort: {sort}, language: {tweet_language})")
        
        run_input = {
            "maxItems": max_items,
            "searchTerms": [query],
            "sort": sort,
            "tweetLanguage": tweet_language
        }
        
        if geocode:
            run_input["geocode"] = geocode
        
        run = client.actor("apidojo/twitter-scraper-lite").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        all_items = list(dataset.items)
        
        results["results"] = all_items[:max_items] if len(all_items) > max_items else all_items
        
        logger.info(f"Found {len(all_items)} results for query: {query}, limiting to {len(results['results'])} (max_items: {max_items})")
        
        if use_cache:
            cache_key = _get_x_cache_key(query, geocode, max_items, sort, tweet_language)
            _save_x_cache(cache_key, results)
            logger.info(f"✅ Cached X results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in X search: {e}", exc_info=True)
        raise

