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

from modules.supabase_connection import get_supabase_client
from modules.tiktok_search import search_tiktok
from modules.google_search import search_google
from modules.instagram_search import search_instagram_term
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
    Only saves if the query doesn't already exist (unless skip_existing=False).
    
    Args:
        client: Apify client instance
        query: Search query
        max_items: Maximum number of results
        search_type: Type of search - "search", "hashtag", or "user"
        country_code: Optional country code for proxy
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        skip_existing: If True, skip saving if meta already exists for this query
        
    Returns:
        ID of the created record in metas table, None if skipped, or None if failed
    """
    try:
        if skip_existing and meta_exists(query, "tiktok", id_company=1):
            logger.info(f"⏭️  Skipping capture for query '{query}' - already exists in database")
            return None
        
        logger.info(f"Capturing TikTok data for query: {query} (type: {search_type})")
        
        results_dict = search_tiktok(
            client=client,
            query=query,
            max_items=max_items,
            search_type=search_type,
            country_code=country_code,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        results = results_dict.get("results", [])
        logger.info(f"Found {len(results)} TikTok results to save")
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "tiktok",
            "query": query,
            "meta": results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved TikTok data to metas table with ID: {record_id}")
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
    """
    try:
        if skip_existing and meta_exists(query, "google", id_company=1):
            logger.info(f"⏭️  Skipping Google capture for query '{query}' - already exists")
            return None
        
        logger.info(f"Capturing Google data for query: {query}")
        
        results = search_google(
            client=client,
            query=query,
            max_items=max_items,
            country_code=country_code,
            language_code=language_code,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        logger.info(f"Found {len(results)} Google results to save")
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "google",
            "query": query,
            "meta": results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved Google data to metas table with ID: {record_id}")
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
    """
    try:
        if skip_existing and meta_exists(query, "instagram", id_company=1):
            logger.info(f"⏭️  Skipping Instagram capture for query '{query}' - already exists")
            return None
        
        logger.info(f"Capturing Instagram data for query: {query}")
        
        results = search_instagram_term(
            client=client,
            term=query,
            limit=limit,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        logger.info(f"Found {len(results)} Instagram results to save")
        
        supabase = get_supabase_client()
        
        data = {
            "id_company": 1,
            "label": "instagram",
            "query": query,
            "meta": results
        }
        
        response = supabase.table("metas").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            record_id = response.data[0]["id"]
            logger.info(f"✅ Saved Instagram data to metas table with ID: {record_id}")
            return record_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error capturing Instagram data: {e}", exc_info=True)
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
    Capture data from all platforms (TikTok, Instagram, Google) for a query.
    
    Args:
        client: Apify client instance
        query: Search query
        platforms: List of platforms to capture (["tiktok", "instagram", "google"]). If None, captures all.
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
        platforms = ["tiktok", "instagram", "google"]
    
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
                
            else:
                logger.warning(f"Unknown platform: {platform}")
                results[platform] = None
                
        except Exception as e:
            logger.error(f"❌ Error capturing {platform}: {e}", exc_info=True)
            results[platform] = None
    
    return results
