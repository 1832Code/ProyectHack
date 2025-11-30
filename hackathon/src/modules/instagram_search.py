"""
Instagram Search Module
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

_instagram_cache_dir = Path("/tmp/instagram_cache")
_cache_max_size = 50
_cache_ttl_hours = 10/24

try:
    _instagram_cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Instagram cache directory initialized: {_instagram_cache_dir}")
except Exception as e:
    logger.error(f"❌ Failed to create Instagram cache directory: {e}", exc_info=True)


def _get_instagram_cache_key(search_type: str, query: str, limit: int, results_type: Optional[str] = None) -> str:
    """Generate a cache key for Instagram results."""
    key_parts = [
        search_type,
        query.lower().strip(),
        str(limit),
        results_type or ""
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _get_instagram_cache_file_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return _instagram_cache_dir / f"{cache_key}.json"


def _load_instagram_cache(cache_key: str) -> Optional[List[Dict[str, Any]]]:
    """Load Instagram results from cache."""
    cache_file = _get_instagram_cache_file_path(cache_key)
    
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
            logger.info(f"Instagram cache entry expired (age: {age.total_seconds()/3600:.1f}h)")
            cache_file.unlink()
            return None
        
        results = cache_data.get('results', [])
        logger.info(f"✅✅✅ INSTAGRAM CACHE HIT - Using cached results (NO APIFY API CALLS - SAVING CREDITS)")
        logger.info(f"   Cache age: {age.total_seconds()/60:.1f} minutes")
        return results
    except Exception as e:
        logger.warning(f"Error loading Instagram cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_instagram_cache(cache_key: str, results: List[Dict[str, Any]]) -> None:
    """Save Instagram results to cache."""
    try:
        cache_file = _get_instagram_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved Instagram cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        _cleanup_old_instagram_cache()
    except Exception as e:
        logger.error(f"Error saving Instagram cache: {e}", exc_info=True)


def _cleanup_old_instagram_cache() -> None:
    """Remove old cache files if cache directory is too large."""
    try:
        cache_files = sorted(
            _instagram_cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if len(cache_files) > _cache_max_size:
            for file_to_remove in cache_files[_cache_max_size:]:
                try:
                    file_to_remove.unlink()
                    logger.info(f"Cleaned up old Instagram cache file: {file_to_remove.name}")
                except Exception as e:
                    logger.warning(f"Error removing cache file {file_to_remove.name}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning up Instagram cache: {e}")


def search_instagram_term(
    client: ApifyClient,
    term: str,
    limit: int = 200,
    results_type: str = "comments",
    search_limit: int = 4,
    use_cache: bool = True,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Instagram by term using Apify.
    
    Args:
        client: Apify client instance
        term: Search term
        limit: Maximum number of results
        results_type: Type of results (comments, posts, etc.)
        search_limit: Search limit
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        List of search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_instagram_cache_key("term", term, limit, results_type)
        cached_results = _load_instagram_cache(cache_key)
        
        if cached_results:
            logger.info(f"✅✅✅ Using cached Instagram term results - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ Instagram cache MISS - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   Instagram cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring Instagram cache")
    
    try:
        logger.info(f"Starting Instagram term search for: {term}")
        
        run_input = {
            "searchType": "term",
            "searchLimit": search_limit,
            "resultsLimit": limit,
            "resultsType": results_type
        }
        
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results = list(dataset.items)
        
        logger.info(f"Found {len(results)} results for term: {term}")
        
        if use_cache:
            cache_key = _get_instagram_cache_key("term", term, limit, results_type)
            _save_instagram_cache(cache_key, results)
            logger.info(f"✅ Cached Instagram term results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in Instagram term search: {e}", exc_info=True)
        raise


def search_instagram_hashtag(
    client: ApifyClient,
    hashtag: str,
    limit: int = 30,
    use_cache: bool = True,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Instagram by hashtag using Apify.
    
    Args:
        client: Apify client instance
        hashtag: Hashtag to search (without #)
        limit: Maximum number of results
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        List of search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_instagram_cache_key("hashtag", hashtag, limit)
        cached_results = _load_instagram_cache(cache_key)
        
        if cached_results:
            logger.info(f"✅✅✅ Using cached Instagram hashtag results - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ Instagram cache MISS - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   Instagram cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring Instagram cache")
    
    try:
        logger.info(f"Starting Instagram hashtag search for: #{hashtag}")
        
        run_input = {
            "searchType": "hashtag",
            "hashtags": [hashtag.replace("#", "")],
            "resultsLimit": limit
        }
        
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results = list(dataset.items)
        
        logger.info(f"Found {len(results)} results for hashtag: #{hashtag}")
        
        if use_cache:
            cache_key = _get_instagram_cache_key("hashtag", hashtag, limit)
            _save_instagram_cache(cache_key, results)
            logger.info(f"✅ Cached Instagram hashtag results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in Instagram hashtag search: {e}", exc_info=True)
        raise


def search_instagram_profile(
    client: ApifyClient,
    username: str,
    limit: int = 30,
    use_cache: bool = True,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Instagram profile using Apify.
    
    Args:
        client: Apify client instance
        username: Instagram username (without @)
        limit: Maximum number of results
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        List of search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_instagram_cache_key("profile", username, limit)
        cached_results = _load_instagram_cache(cache_key)
        
        if cached_results:
            logger.info(f"✅✅✅ Using cached Instagram profile results - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ Instagram cache MISS - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   Instagram cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring Instagram cache")
    
    try:
        logger.info(f"Starting Instagram profile search for: @{username}")
        
        run_input = {
            "searchType": "profile",
            "usernames": [username.replace("@", "")],
            "resultsLimit": limit
        }
        
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results = list(dataset.items)
        
        logger.info(f"Found {len(results)} results for profile: @{username}")
        
        if use_cache:
            cache_key = _get_instagram_cache_key("profile", username, limit)
            _save_instagram_cache(cache_key, results)
            logger.info(f"✅ Cached Instagram profile results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in Instagram profile search: {e}", exc_info=True)
        raise

