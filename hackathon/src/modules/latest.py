"""
Latest Module for Processing Meta Data
Author: Mauricio J. @synaw_w
"""

import logging
from typing import List, Optional, Dict, Any

from modules.capture import get_meta
from modules.supabase_connection import get_supabase_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_meta_data(meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a single meta record and extract data for posts table.
    
    Args:
        meta: Meta record as dictionary
        
    Returns:
        Dict with processed data ready for Post model, or None if processing fails
    """
    try:
        logger.info(f"Processing meta ID: {meta.get('id')}, label: {meta.get('label')}, query: {meta.get('query')}")
        
        meta_data = meta.get("meta", {})
        
        processed = {
            "id_company": meta.get("id_company", 1),
            "title": None,
            "description": None,
            "insight1": None,
            "insight2": None,
            "insight3": None,
            "sentiment": None,
            "image": None,
            "video": None
        }
        
        label = meta.get("label", "")
        
        if label == "tiktok":
            processed = _process_tiktok_data(meta_data, processed)
        elif label == "instagram":
            processed = _process_instagram_data(meta_data, processed)
        elif label == "google":
            processed = _process_google_data(meta_data, processed)
        else:
            logger.warning(f"Unknown label: {label}")
            return None
        
        logger.info(f"✅ Processed meta ID: {meta.get('id')}")
        return processed
        
    except Exception as e:
        logger.error(f"❌ Error processing meta ID {meta.get('id')}: {e}", exc_info=True)
        return None


def _process_tiktok_data(meta_data: Any, processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process TikTok data structure."""
    if isinstance(meta_data, list) and len(meta_data) > 0:
        first_item = meta_data[0]
        
        if isinstance(first_item, dict):
            text = first_item.get("text", "")
            if text:
                processed["title"] = text[:500] if len(text) > 500 else text
                processed["description"] = text[:2000] if len(text) > 2000 else text
            
            processed["video"] = first_item.get("webVideoUrl")
            processed["image"] = first_item.get("authorMeta.avatar")
            
            play_count = first_item.get("playCount", 0)
            digg_count = first_item.get("diggCount", 0)
            share_count = first_item.get("shareCount", 0)
            comment_count = first_item.get("commentCount", 0)
            collect_count = first_item.get("collectCount", 0)
            
            processed["insight1"] = float(play_count) if play_count else None
            processed["insight2"] = float(digg_count) if digg_count else None
            processed["insight3"] = float(share_count) if share_count else None
            
            total_engagement = (
                (processed["insight1"] or 0) +
                (processed["insight2"] or 0) +
                (processed["insight3"] or 0) +
                (float(comment_count) if comment_count else 0) +
                (float(collect_count) if collect_count else 0)
            )
            
            if total_engagement > 0:
                processed["sentiment"] = min(100.0, (total_engagement / 1000000.0) * 100.0)
    
    return processed


def _process_instagram_data(meta_data: Any, processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process Instagram data structure."""
    if isinstance(meta_data, list) and len(meta_data) > 0:
        first_item = meta_data[0]
        
        if isinstance(first_item, dict):
            processed["title"] = first_item.get("caption", "")[:500] if first_item.get("caption") else None
            processed["description"] = first_item.get("caption", "")[:2000] if first_item.get("caption") else None
            processed["image"] = first_item.get("displayUrl") or first_item.get("url")
            processed["video"] = first_item.get("videoUrl")
            
            processed["insight1"] = float(first_item.get("likesCount", 0)) if first_item.get("likesCount") else None
            processed["insight2"] = float(first_item.get("commentsCount", 0)) if first_item.get("commentsCount") else None
            processed["insight3"] = float(first_item.get("timestamp", 0)) if first_item.get("timestamp") else None
    
    return processed


def _process_google_data(meta_data: Any, processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process Google data structure."""
    if isinstance(meta_data, list) and len(meta_data) > 0:
        first_item = meta_data[0]
        
        if isinstance(first_item, dict):
            processed["title"] = first_item.get("title", "")[:500] if first_item.get("title") else None
            processed["description"] = first_item.get("description", "")[:2000] if first_item.get("description") else None
            processed["image"] = None
            processed["video"] = None
    
    return processed


def get_posts(id_company: int = 1, limit: int = 100, order_by: str = "created_at") -> List[Dict[str, Any]]:
    """
    Get posts from the database.
    
    Args:
        id_company: Company ID (default: 1)
        limit: Maximum number of posts to return
        order_by: Field to order by (default: "created_at")
        
    Returns:
        List of post records as dictionaries
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("posts").select("*").eq("id_company", id_company)
        
        query = query.order(order_by, desc=True).limit(limit)
        
        response = query.execute()
        
        results = response.data if response.data else []
        logger.info(f"✅ Retrieved {len(results)} posts")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error getting posts: {e}", exc_info=True)
        return []


def save_post(processed_data: Dict[str, Any]) -> Optional[int]:
    """
    Save processed data to posts table.
    
    Args:
        processed_data: Dict with processed data for Post model
        
    Returns:
        ID of the created post record, or None if failed
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("posts").insert(processed_data).execute()
        
        if response.data and len(response.data) > 0:
            post_id = response.data[0]["id"]
            logger.info(f"✅ Saved post to database with ID: {post_id}")
            return post_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error saving post: {e}", exc_info=True)
        return None


def process_latest_metas(id_company: int = 1, label: Optional[str] = None, limit: int = 100) -> List[int]:
    """
    Get latest metas, process them, and save to posts table.
    
    Args:
        id_company: Company ID (default: 1)
        label: Optional label filter (e.g., "tiktok", "instagram", "google")
        limit: Maximum number of metas to process
        
    Returns:
        List of created post IDs
    """
    try:
        logger.info(f"Processing latest metas (company: {id_company}, label: {label}, limit: {limit})")
        
        metas = get_meta(id_company=id_company, label=label, limit=limit)
        
        if not metas:
            logger.warning("No metas found to process")
            return []
        
        created_posts = []
        
        for meta in metas:
            processed_data = process_meta_data(meta)
            
            if processed_data:
                post_id = save_post(processed_data)
                if post_id:
                    created_posts.append(post_id)
        
        logger.info(f"✅ Processed {len(created_posts)} posts from {len(metas)} metas")
        return created_posts
        
    except Exception as e:
        logger.error(f"❌ Error processing latest metas: {e}", exc_info=True)
        return []
