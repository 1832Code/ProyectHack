"""
Latest Module for Processing Meta Data
Author: Mauricio J. @synaw_w
"""

import logging
from typing import List, Optional, Dict, Any

from src.modules.capture import get_meta
from src.modules.supabase_connection import get_supabase_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _clean_url(url: Optional[str]) -> Optional[str]:
    """Clean URL by removing newlines, carriage returns, and tabs."""
    if not url:
        return None
    return str(url).strip().replace("\n", "").replace("\r", "").replace("\t", "")


def process_meta_data(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a single meta record and extract data for posts table.
    Returns a list of processed posts (one per item in meta data).
    
    Args:
        meta: Meta record as dictionary
        
    Returns:
        List of dicts with processed data ready for Post model, or empty list if processing fails
    """
    try:
        logger.info(f"Processing meta ID: {meta.get('id')}, label: {meta.get('label')}, query: {meta.get('query')}")
        
        meta_data = meta.get("meta", {})
        label = meta.get("label", "")
        id_company = meta.get("id_company", 1)
        query = meta.get("query", "")
        
        logger.info(f"Meta data type: {type(meta_data)}, length: {len(meta_data) if isinstance(meta_data, (list, dict)) else 'N/A'}")
        
        if not isinstance(meta_data, list):
            if isinstance(meta_data, dict):
                logger.warning(f"Meta data is a dict, not a list. Keys: {list(meta_data.keys())[:5]}")
                if "results" in meta_data:
                    meta_data = meta_data["results"]
                    logger.info(f"Found 'results' key, using that. New length: {len(meta_data) if isinstance(meta_data, list) else 'N/A'}")
                else:
                    logger.error(f"Meta data is a dict but no 'results' key found. Cannot process.")
                    return []
            else:
                logger.warning(f"Meta data is not a list or dict for meta ID: {meta.get('id')}, type: {type(meta_data)}")
                return []
        
        if len(meta_data) == 0:
            logger.warning(f"Meta data list is empty for meta ID: {meta.get('id')}")
            return []
        
        logger.info(f"Processing {len(meta_data)} items from meta ID: {meta.get('id')} with query: '{query}'")
        
        processed_posts = []
        skipped_items = 0
        
        for idx, item in enumerate(meta_data):
            processed = {
                "id_company": id_company,
                "query": query,
                "title": None,
                "description": None,
                "insight1": None,
                "insight2": None,
                "insight3": None,
                "sentiment": None,
                "image": None,
                "video": None
            }
            
            if label == "tiktok":
                processed = _process_tiktok_data(item, processed)
            elif label == "instagram":
                processed = _process_instagram_data(item, processed)
            elif label == "google":
                processed = _process_google_data(item, processed)
            else:
                logger.warning(f"Unknown label: {label}")
                skipped_items += 1
                continue
            
            if processed.get("title") or processed.get("video"):
                processed_posts.append(processed)
            else:
                skipped_items += 1
                logger.debug(f"Skipped item {idx}: no title or video")
        
        logger.info(f"✅ Processed meta ID: {meta.get('id')} - {len(processed_posts)} posts extracted from {len(meta_data)} items (skipped {skipped_items})")
        return processed_posts
        
    except Exception as e:
        logger.error(f"❌ Error processing meta ID {meta.get('id')}: {e}", exc_info=True)
        return []


def _process_tiktok_data(item: Dict[str, Any], processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process TikTok data item (single video)."""
    if isinstance(item, dict):
        text = item.get("text", "")
        if text:
            processed["title"] = text[:500] if len(text) > 500 else text
            processed["description"] = text[:2000] if len(text) > 2000 else text
        
        processed["video"] = _clean_url(item.get("webVideoUrl"))
        
        author_meta = item.get("authorMeta", {})
        if isinstance(author_meta, dict):
            image_url = author_meta.get("avatar")
        else:
            image_url = item.get("authorMeta.avatar")
        
        processed["image"] = _clean_url(image_url)
        
        play_count = item.get("playCount", 0)
        digg_count = item.get("diggCount", 0)
        share_count = item.get("shareCount", 0)
        comment_count = item.get("commentCount", 0)
        collect_count = item.get("collectCount", 0)
        
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


def _process_instagram_data(item: Dict[str, Any], processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process Instagram data item (single post)."""
    if isinstance(item, dict):
        processed["title"] = item.get("caption", "")[:500] if item.get("caption") else None
        processed["description"] = item.get("caption", "")[:2000] if item.get("caption") else None
        
        processed["image"] = _clean_url(item.get("displayUrl") or item.get("url"))
        processed["video"] = _clean_url(item.get("videoUrl"))
        
        processed["insight1"] = float(item.get("likesCount", 0)) if item.get("likesCount") else None
        processed["insight2"] = float(item.get("commentsCount", 0)) if item.get("commentsCount") else None
        processed["insight3"] = float(item.get("timestamp", 0)) if item.get("timestamp") else None
    
    return processed


def _process_google_data(item: Dict[str, Any], processed: Dict[str, Any]) -> Dict[str, Any]:
    """Process Google data item (single search result)."""
    if isinstance(item, dict):
        processed["title"] = item.get("title", "")[:500] if item.get("title") else None
        processed["description"] = item.get("description", "")[:2000] if item.get("description") else None
        processed["image"] = None
        processed["video"] = None
    
    return processed


def post_exists(title: str, video: Optional[str] = None, id_company: int = 1) -> bool:
    """
    Check if a post already exists with the same title and video.
    
    Args:
        title: Post title
        video: Post video URL (optional)
        id_company: Company ID (default: 1)
        
    Returns:
        True if post exists, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        clean_title = title.strip().replace("\n", "").replace("\r", "") if title else ""
        query = supabase.table("posts").select("id").eq("id_company", id_company).eq("title", clean_title)
        
        if video:
            clean_video = _clean_url(video)
            if clean_video:
                query = query.eq("video", clean_video)
        
        response = query.limit(1).execute()
        
        exists = len(response.data) > 0
        if exists:
            logger.info(f"✅ Post already exists (title: '{title[:50]}...', id: {response.data[0]['id']})")
        else:
            logger.info(f"ℹ️  No existing post found (title: '{title[:50]}...')")
        
        return exists
        
    except Exception as e:
        logger.error(f"❌ Error checking post existence: {e}", exc_info=True)
        return False


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
        logger.info(f"🔍 get_posts called: id_company={id_company}, limit={limit}, order_by={order_by}")
        
        supabase = get_supabase_client()
        logger.info("✅ Supabase client obtained")
        
        query = supabase.table("posts").select("*").eq("id_company", id_company)
        logger.info(f"✅ Query built for id_company={id_company}")
        
        query = query.order(order_by, desc=True).limit(limit)
        logger.info(f"✅ Query ordered by {order_by} desc, limit={limit}")
        
        response = query.execute()
        logger.info(f"✅ Query executed, response received")
        
        results = response.data if response.data else []
        logger.info(f"✅ Retrieved {len(results)} posts from database")
        
        if len(results) == 0:
            logger.warning(f"⚠️  No posts found for id_company={id_company}")
        else:
            logger.info(f"📊 First post ID: {results[0].get('id') if results else 'N/A'}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error getting posts: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []


def save_post(processed_data: Dict[str, Any], skip_existing: bool = True) -> Optional[int]:
    """
    Save processed data to posts table.
    Only saves if the post doesn't already exist (unless skip_existing=False).
    
    Args:
        processed_data: Dict with processed data for Post model
        skip_existing: If True, skip saving if post already exists
        
    Returns:
        ID of the created post record, None if skipped, or None if failed
    """
    try:
        title = processed_data.get("title")
        video = _clean_url(processed_data.get("video"))
        image = _clean_url(processed_data.get("image"))
        id_company = processed_data.get("id_company", 1)
        
        processed_data["video"] = video
        processed_data["image"] = image
        
        if skip_existing and title:
            if post_exists(title, video, id_company):
                logger.debug(f"⏭️  Skipping post save - already exists (title: '{title[:50]}...', video: {video[:50] if video else 'None'}...)")
                return None
        
        supabase = get_supabase_client()
        
        response = supabase.table("posts").insert(processed_data).execute()
        
        if response.data and len(response.data) > 0:
            post_id = response.data[0]["id"]
            logger.debug(f"✅ Saved post to database with ID: {post_id} (title: '{title[:50] if title else 'None'}...')")
            return post_id
        else:
            logger.error("❌ No data returned from insert")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error saving post: {e}", exc_info=True)
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            logger.info(f"⏭️  Post already exists (database constraint): {e}")
            return None
        return None


def process_latest_metas(id_company: int = 1, label: Optional[str] = None, limit: int = 100) -> List[int]:
    """
    Get latest metas, process them, and save to posts table.
    Only saves posts that don't already exist.
    
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
        skipped_posts = 0
        
        logger.info(f"Processing {len(metas)} meta(s)")
        
        for meta in metas:
            processed_posts_list = process_meta_data(meta)
            logger.info(f"Meta ID {meta.get('id')} produced {len(processed_posts_list)} processed posts")
            
            for processed_data in processed_posts_list:
                if processed_data:
                    post_id = save_post(processed_data, skip_existing=True)
                    if post_id:
                        created_posts.append(post_id)
                    else:
                        skipped_posts += 1
        
        logger.info(f"✅ Processed {len(created_posts)} new posts from {len(metas)} metas (skipped {skipped_posts} duplicates)")
        return created_posts
        
    except Exception as e:
        logger.error(f"❌ Error processing latest metas: {e}", exc_info=True)
        return []
