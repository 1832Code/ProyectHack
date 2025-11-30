"""
Supabase Connection Module
Author: Mauricio J. @synaw_w
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    
    Returns:
        Supabase Client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url:
                raise ValueError("SUPABASE_URL environment variable is not set")
            
            if not supabase_key:
                raise ValueError("SUPABASE_KEY environment variable is not set")
            
            supabase_url = str(supabase_url).strip().replace("\n", "").replace("\r", "").replace("\t", "")
            supabase_key = str(supabase_key).strip().replace("\n", "").replace("\r", "").replace("\t", "")
            
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Supabase client: {e}", exc_info=True)
            raise
    
    return _supabase_client
