"""
TikTok Search Module
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

_tiktok_cache_dir = Path("/tmp/tiktok_cache")
_cache_max_size = 50
_cache_ttl_hours = 24

try:
    _tiktok_cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ TikTok cache directory initialized: {_tiktok_cache_dir}")
except Exception as e:
    logger.error(f"❌ Failed to create TikTok cache directory: {e}", exc_info=True)


def _get_tiktok_cache_key(query: str, search_type: str, country_code: Optional[str], max_items: int) -> str:
    """Generate a cache key for TikTok results."""
    key_parts = [
        query.lower().strip(),
        search_type,
        country_code or "",
        str(max_items)
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _get_tiktok_cache_file_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return _tiktok_cache_dir / f"{cache_key}.json"


def _load_tiktok_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Load TikTok results from cache."""
    cache_file = _get_tiktok_cache_file_path(cache_key)
    
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
            logger.info(f"TikTok cache entry expired (age: {age.total_seconds()/3600:.1f}h)")
            cache_file.unlink()
            return None
        
        results = cache_data.get('results', {})
        logger.info(f"✅✅✅ TIKTOK CACHE HIT - Using cached results (NO APIFY API CALLS - SAVING CREDITS)")
        logger.info(f"   Cache age: {age.total_seconds()/60:.1f} minutes")
        return results
    except Exception as e:
        logger.warning(f"Error loading TikTok cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_tiktok_cache(cache_key: str, results: Dict[str, Any]) -> None:
    """Save TikTok results to cache."""
    try:
        cache_file = _get_tiktok_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved TikTok cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        _cleanup_old_tiktok_cache()
    except Exception as e:
        logger.error(f"Error saving TikTok cache: {e}", exc_info=True)


def _cleanup_old_tiktok_cache() -> None:
    """Remove old cache files if cache directory is too large."""
    try:
        cache_files = sorted(
            _tiktok_cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        if len(cache_files) > _cache_max_size:
            for file_to_remove in cache_files[_cache_max_size:]:
                try:
                    file_to_remove.unlink()
                    logger.info(f"Cleaned up old TikTok cache file: {file_to_remove.name}")
                except Exception as e:
                    logger.warning(f"Error removing cache file {file_to_remove.name}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning up TikTok cache: {e}")


def search_tiktok(
    client: ApifyClient,
    query: str,
    max_items: int = 30,
    search_type: str = "search",
    country_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Search TikTok content using Apify actor clockworks/tiktok-scraper.
    
    Args:
        client: Apify client instance
        query: Search query (hashtag, username, or search term)
        max_items: Maximum number of results
        search_type: Type of search - "search", "hashtag", or "user"
        country_code: Optional country code for proxy (e.g., "PE", "US")
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        Dict containing search results
    """
    if use_cache and not force_refresh:
        cache_key = _get_tiktok_cache_key(query, search_type, country_code, max_items)
        logger.info(f"🔍 Looking for TikTok cache with key: {cache_key[:16]}... (query: '{query}', max_items: {max_items})")
        cached_results = _load_tiktok_cache(cache_key)
        
        if cached_results:
            cached_results_list = cached_results.get("results", [])
            logger.info(f"📦 Cache found with {len(cached_results_list)} items, requested: {max_items}")
            if len(cached_results_list) > max_items:
                logger.info(f"✅✅✅ Using cached TikTok results - limiting from {len(cached_results_list)} to {max_items} - NO APIFY API CALLS")
                cached_results["results"] = cached_results_list[:max_items]
            else:
                logger.info(f"✅✅✅ Using cached TikTok results ({len(cached_results_list)} items) - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ TikTok cache MISS for max_items={max_items} - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   TikTok cache key: {cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring TikTok cache")
    
    results = {
        "query": query,
        "search_type": search_type,
        "results": []
    }
    
    try:
        logger.info(f"Starting TikTok search for: {query} (type: {search_type}, max_items: {max_items}, country: {country_code})")
        
        run_input = {
            "excludePinnedPosts": False,
            "resultsPerPage": min(max_items, 100),
            "scrapeRelatedVideos": False,
            "shouldDownloadAvatars": False,
            "shouldDownloadCovers": False,
            "shouldDownloadMusicCovers": False,
            "shouldDownloadSlideshowImages": True,
            "shouldDownloadSubtitles": False,
            "shouldDownloadVideos": False
        }
        
        if country_code:
            run_input["proxyCountryCode"] = country_code
        
        if search_type == "hashtag":
            hashtag = query.replace("#", "").strip()
            run_input["hashtags"] = [hashtag]
        elif search_type == "user":
            username = query.replace("@", "").strip()
            run_input["usernames"] = [username]
        else:
            run_input["searchQueries"] = [query]
        
        run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        all_items = list(dataset.items)
        
        results["results"] = all_items[:max_items] if len(all_items) > max_items else all_items
        
        logger.info(f"Found {len(all_items)} results for query: {query}, limiting to {len(results['results'])} (max_items: {max_items})")
        
        if use_cache:
            cache_key = _get_tiktok_cache_key(query, search_type, country_code, max_items)
            _save_tiktok_cache(cache_key, results)
            logger.info(f"✅ Cached TikTok results for future requests")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in TikTok search: {e}", exc_info=True)
        raise

