"""
Capture Module for Social Media Data
Author: Mauricio J. @synaw_w
"""

import os
import logging
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.modules.supabase_connection import get_supabase_client
from src.modules.tiktok_search import search_tiktok
from src.modules.google_search import search_google
from src.modules.x_search import search_x
from src.modules.instagram_search import search_instagram_term
from apify_client import ApifyClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def meta_exists(query: str, label: str, id_company: int = 1) -> bool:
    """
    Check if a meta record already exists with the same query and label.
    
    Args:
        query: Search query
        label: Label (e.g., "tiktok", "instagram", "google")
        id_company: Company ID (default: 1)
        
    Returns:
        True if meta exists, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("metas").select("id").eq("query", query).eq("label", label).eq("id_company", id_company).limit(1).execute()
        
        exists = len(response.data) > 0
        if exists:
            logger.info(f"✅ Meta already exists for query: '{query}' (label: {label}, id: {response.data[0]['id']})")
        else:
            logger.info(f"ℹ️  No existing meta found for query: '{query}' (label: {label})")
        
        return exists
        
    except Exception as e:
        logger.error(f"❌ Error checking meta existence: {e}", exc_info=True)
        return False


def get_meta(meta_id: Optional[int] = None, id_company: int = 1, label: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get meta records from the database.
    
    Args:
        meta_id: Optional specific meta ID to retrieve
        id_company: Company ID (default: 1)
        label: Optional label filter (e.g., "tiktok", "instagram", "google")
        limit: Maximum number of records to return
        
    Returns:
        List of meta records as dictionaries
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("metas").select("*").eq("id_company", id_company)
        
        if meta_id:
            query = query.eq("id", meta_id)
        
        if label:
            query = query.eq("label", label)
        
        query = query.order("created_at", desc=True).limit(limit)
        
        response = query.execute()
        
        results = response.data if response.data else []
        logger.info(f"✅ Retrieved {len(results)} meta records")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error getting meta records: {e}", exc_info=True)
        return []


def capture_tiktok(
    client: ApifyClient,
    query: str,
    max_items: int = 30,
    search_type: str = "search",
    country_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False,
    skip_existing: bool = True
) -> Optional[int]:
    """
    Capture TikTok data and save to metas table.
    Always makes the API call, but only saves new results.
    
    Args:
        client: Apify client instance
        query: Search query
        max_items: Maximum number of results
        search_type: Type of search - "search", "hashtag", or "user"
        country_code: Optional country code for proxy
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        skip_existing: If True, only save if there are new results
        
    Returns:
        ID of the created record in metas table, None if no new results or failed
    """
    try:
        logger.info(f"🔍 Always making API call for TikTok query: {query} (type: {search_type})")
        
        results_dict = search_tiktok(
            client=client,
            query=query,
            max_items=max_items,
            search_type=search_type,
            country_code=country_code,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        new_results = results_dict.get("results", [])
        logger.info(f"📥 Received {len(new_results)} TikTok results from API")
        
        if skip_existing:
            existing_metas = get_meta(id_company=1, label="tiktok", limit=100)
            existing_video_urls = set()
            
            for meta in existing_metas:
                if meta.get("query") == query:
                    meta_data = meta.get("meta", [])
                    if isinstance(meta_data, list):
                        for item in meta_data:
                            video_url = item.get("webVideoUrl") if isinstance(item, dict) else None
                            if video_url:
                                existing_video_urls.add(video_url)
            
            logger.info(f"📊 Found {len(existing_video_urls)} existing videos for query: {query}")
            
            filtered_results = []
            for item in new_results:
                if isinstance(item, dict):
                    video_url = item.get("webVideoUrl")
                    if video_url and video_url not in existing_video_urls:
                        filtered_results.append(item)
            
            if len(filtered_results) == 0:
                logger.info(f"⏭️  No new TikTok results for query '{query}' - all {len(new_results)} results already exist")
                return None
            
            logger.info(f"✅ Found {len(filtered_results)} new TikTok results (out of {len(new_results)}")
            new_results = filtered_results
        
        if len(new_results) == 0:
            logger.info(f"⏭️  No TikTok results to save for query: {query}")
            return None
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "tiktok",
            "query": query,
            "meta": new_results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved {len(new_results)} new TikTok results to metas table with ID: {record_id}")
            return record_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error capturing TikTok data: {e}", exc_info=True)
        return None


def capture_google(
    client: ApifyClient,
    query: str,
    max_items: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False,
    skip_existing: bool = True
) -> Optional[int]:
    """
    Capture Google search data and save to metas table.
    Always makes the API call, but only saves new results.
    """
    try:
        logger.info(f"🔍 Always making API call for Google query: {query}")
        
        new_results = search_google(
            client=client,
            query=query,
            max_items=max_items,
            country_code=country_code,
            language_code=language_code,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        logger.info(f"📥 Received {len(new_results)} Google results from API")
        
        if skip_existing:
            existing_metas = get_meta(id_company=1, label="google", limit=100)
            existing_urls = set()
            
            for meta in existing_metas:
                if meta.get("query") == query:
                    meta_data = meta.get("meta", [])
                    if isinstance(meta_data, list):
                        for item in meta_data:
                            url = item.get("url") if isinstance(item, dict) else None
                            if url:
                                existing_urls.add(url)
            
            logger.info(f"📊 Found {len(existing_urls)} existing Google URLs for query: {query}")
            
            filtered_results = []
            for item in new_results:
                if isinstance(item, dict):
                    url = item.get("url")
                    if url and url not in existing_urls:
                        filtered_results.append(item)
            
            if len(filtered_results) == 0:
                logger.info(f"⏭️  No new Google results for query '{query}' - all {len(new_results)} results already exist")
                return None
            
            logger.info(f"✅ Found {len(filtered_results)} new Google results (out of {len(new_results)})")
            new_results = filtered_results
        
        if len(new_results) == 0:
            logger.info(f"⏭️  No Google results to save for query: {query}")
            return None
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "google",
            "query": query,
            "meta": new_results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved {len(new_results)} new Google results to metas table with ID: {record_id}")
            return record_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error capturing Google data: {e}", exc_info=True)
        return None


def capture_instagram(
    client: ApifyClient,
    query: str,
    limit: int = 30,
    use_cache: bool = True,
    force_refresh: bool = False,
    skip_existing: bool = True
) -> Optional[int]:
    """
    Capture Instagram data and save to metas table.
    Always makes the API call, but only saves new results.
    """
    try:
        logger.info(f"🔍 Always making API call for Instagram query: {query}")
        
        new_results = search_instagram_term(
            client=client,
            term=query,
            limit=limit,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        logger.info(f"📥 Received {len(new_results)} Instagram results from API")
        
        if skip_existing:
            existing_metas = get_meta(id_company=1, label="instagram", limit=100)
            existing_urls = set()
            
            for meta in existing_metas:
                if meta.get("query") == query:
                    meta_data = meta.get("meta", [])
                    if isinstance(meta_data, list):
                        for item in meta_data:
                            url = item.get("url") or item.get("displayUrl") if isinstance(item, dict) else None
                            if url:
                                existing_urls.add(url)
            
            logger.info(f"📊 Found {len(existing_urls)} existing Instagram URLs for query: {query}")
            
            filtered_results = []
            for item in new_results:
                if isinstance(item, dict):
                    url = item.get("url") or item.get("displayUrl")
                    if url and url not in existing_urls:
                        filtered_results.append(item)
            
            if len(filtered_results) == 0:
                logger.info(f"⏭️  No new Instagram results for query '{query}' - all {len(new_results)} results already exist")
                return None
            
            logger.info(f"✅ Found {len(filtered_results)} new Instagram results (out of {len(new_results)})")
            new_results = filtered_results
        
        if len(new_results) == 0:
            logger.info(f"⏭️  No Instagram results to save for query: {query}")
            return None
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "instagram",
            "query": query,
            "meta": new_results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved {len(new_results)} new Instagram results to metas table with ID: {record_id}")
            return record_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error capturing Instagram data: {e}", exc_info=True)
        return None


def capture_x(
    client: ApifyClient,
    query: str,
    max_items: int = 1000,
    geocode: Optional[str] = None,
    sort: str = "Latest",
    tweet_language: str = "es",
    use_cache: bool = True,
    force_refresh: bool = False,
    skip_existing: bool = True
) -> Optional[int]:
    """
    Capture X (Twitter) data and save to metas table.
    Always makes the API call, but only saves new results.
    """
    try:
        logger.info(f"🔍 Always making API call for X query: {query}")
        
        results_dict = search_x(
            client=client,
            query=query,
            max_items=max_items,
            geocode=geocode,
            sort=sort,
            tweet_language=tweet_language,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        new_results = results_dict.get("results", [])
        logger.info(f"📥 Received {len(new_results)} X results from API")
        
        if skip_existing:
            existing_metas = get_meta(id_company=1, label="x", limit=100)
            existing_tweet_ids = set()
            
            for meta in existing_metas:
                if meta.get("query") == query:
                    meta_data = meta.get("meta", [])
                    if isinstance(meta_data, list):
                        for item in meta_data:
                            tweet_id = item.get("id") or item.get("tweetId") if isinstance(item, dict) else None
                            if tweet_id:
                                existing_tweet_ids.add(str(tweet_id))
            
            logger.info(f"📊 Found {len(existing_tweet_ids)} existing X tweets for query: {query}")
            
            filtered_results = []
            for item in new_results:
                if isinstance(item, dict):
                    tweet_id = item.get("id") or item.get("tweetId")
                    if tweet_id and str(tweet_id) not in existing_tweet_ids:
                        filtered_results.append(item)
            
            if len(filtered_results) == 0:
                logger.info(f"⏭️  No new X results for query '{query}' - all {len(new_results)} results already exist")
                return None
            
            logger.info(f"✅ Found {len(filtered_results)} new X results (out of {len(new_results)})")
            new_results = filtered_results
        
        if len(new_results) == 0:
            logger.info(f"⏭️  No X results to save for query: {query}")
            return None
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "x",
            "query": query,
            "meta": new_results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved {len(new_results)} new X results to metas table with ID: {record_id}")
            return record_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error capturing X data: {e}", exc_info=True)
        return None


def capture_all(
    client: ApifyClient,
    query: str,
    platforms: Optional[List[str]] = None,
    max_items: int = 30,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False,
    skip_existing: bool = True
) -> Dict[str, Optional[int]]:
    """
    Capture data from all platforms (TikTok, Instagram, Google, X) for a query.
    
    Args:
        client: Apify client instance
        query: Search query
        platforms: List of platforms to capture (["tiktok", "instagram", "google", "x"]). If None, captures all.
        max_items: Maximum number of results per platform
        country_code: Optional country code
        language_code: Optional language code
        use_cache: Whether to use cache
        force_refresh: Force refresh ignoring cache
        skip_existing: Skip if query already exists
        
    Returns:
        Dict with platform names as keys and meta IDs as values (None if skipped or failed)
    """
    if platforms is None:
        platforms = ["tiktok", "instagram", "google", "x"]
    
    results = {}
    
    for platform in platforms:
        try:
            if platform == "tiktok":
                meta_id = capture_tiktok(
                    client=client,
                    query=query,
                    max_items=max_items,
                    search_type="search",
                    country_code=country_code,
                    use_cache=use_cache,
                    force_refresh=force_refresh,
                    skip_existing=skip_existing
                )
                results["tiktok"] = meta_id
                
            elif platform == "instagram":
                meta_id = capture_instagram(
                    client=client,
                    query=query,
                    limit=max_items,
                    use_cache=use_cache,
                    force_refresh=force_refresh,
                    skip_existing=skip_existing
                )
                results["instagram"] = meta_id
                
            elif platform == "google":
                meta_id = capture_google(
                    client=client,
                    query=query,
                    max_items=max_items,
                    country_code=country_code,
                    language_code=language_code,
                    use_cache=use_cache,
                    force_refresh=force_refresh,
                    skip_existing=skip_existing
                )
                results["google"] = meta_id
                
            elif platform == "x":
                meta_id = capture_x(
                    client=client,
                    query=query,
                    max_items=max_items,
                    geocode=None,
                    sort="Latest",
                    tweet_language=language_code or "es",
                    use_cache=use_cache,
                    force_refresh=force_refresh,
                    skip_existing=skip_existing
                )
                results["x"] = meta_id
                
            else:
                logger.warning(f"Unknown platform: {platform}")
                results[platform] = None
                
        except Exception as e:
            logger.error(f"❌ Error capturing {platform}: {e}", exc_info=True)
            results[platform] = None
    
    return results
