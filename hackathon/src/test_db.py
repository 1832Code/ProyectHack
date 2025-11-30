"""
Database Connection Test Script
Author: Mauricio J. @synaw_w
"""

import os
import sys
import logging
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_supabase_connection():
    """Test Supabase connection using Supabase client."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Supabase Connection (Supabase Client)")
        logger.info("=" * 60)
        
        from modules.supabase_connection import get_supabase_client
        
        supabase = get_supabase_client()
        logger.info("✅ Supabase client created successfully")
        
        response = supabase.table("metas").select("count", count="exact").limit(1).execute()
        logger.info(f"✅ Connection successful - can query database")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Supabase connection: {e}", exc_info=True)
        return False


def test_sqlalchemy_connection():
    """Test Supabase connection using Supabase client (replaces SQLAlchemy)."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Supabase Connection (Supabase Client - Table Access)")
        logger.info("=" * 60)
        
        from modules.supabase_connection import get_supabase_client
        
        supabase = get_supabase_client()
        logger.info("✅ Supabase client created")
        
        response = supabase.table("metas").select("id", count="exact").limit(1).execute()
        count = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
        logger.info(f"✅ Total records in 'metas' table: {count}")
        
        response = supabase.table("posts").select("id", count="exact").limit(1).execute()
        count = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
        logger.info(f"✅ Total records in 'posts' table: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Supabase table access: {e}", exc_info=True)
        return False


def test_tables_exist():
    """Test if required tables exist."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Database Tables")
        logger.info("=" * 60)
        
        from modules.supabase_connection import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            response = supabase.table("metas").select("id", count="exact").limit(1).execute()
            count = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
            logger.info(f"✅ Table 'metas' exists - {count} records")
        except Exception as e:
            logger.error(f"❌ Table 'metas' error: {e}")
            return False
        
        try:
            response = supabase.table("posts").select("id", count="exact").limit(1).execute()
            count = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
            logger.info(f"✅ Table 'posts' exists - {count} records")
        except Exception as e:
            logger.error(f"❌ Table 'posts' error: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing tables: {e}", exc_info=True)
        return False


def test_environment_variables():
    """Test if required environment variables are set."""
    logger.info("=" * 60)
    logger.info("Testing Environment Variables")
    logger.info("=" * 60)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    logger.info(f"Checking SUPABASE_URL...")
    logger.info(f"   Value: {'✅ Set' if supabase_url else '❌ Not set'}")
    if supabase_url:
        logger.info(f"   URL: {supabase_url[:50]}...")
    else:
        logger.error("❌ SUPABASE_URL is not set")
        logger.error("   Please set it in your .env file or environment:")
        logger.error("   export SUPABASE_URL='https://your-project.supabase.co'")
        return False
    
    logger.info(f"Checking SUPABASE_KEY...")
    logger.info(f"   Value: {'✅ Set' if supabase_key else '❌ Not set'}")
    if supabase_key:
        logger.info(f"   Key length: {len(supabase_key)} characters")
    else:
        logger.error("❌ SUPABASE_KEY is not set")
        logger.error("   Please set it in your .env file or environment:")
        logger.error("   export SUPABASE_KEY='your-anon-key'")
        return False
    
    logger.info("")
    logger.info("💡 Tip: Create a .env file in hackathon/ directory with:")
    logger.info("   SUPABASE_URL=https://your-project.supabase.co")
    logger.info("   SUPABASE_KEY=your-anon-key")
    logger.info("")
    
    return True


def test_connection_string():
    """Test Supabase client initialization."""
    try:
        logger.info("=" * 60)
        logger.info("Testing Supabase Client Initialization")
        logger.info("=" * 60)
        
        from modules.supabase_connection import get_supabase_client
        
        supabase = get_supabase_client()
        
        if supabase:
            logger.info("✅ Supabase client initialized successfully")
            logger.info(f"   Client type: {type(supabase).__name__}")
            return True
        else:
            logger.error("❌ Failed to initialize Supabase client")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error initializing Supabase client: {e}", exc_info=True)
        return False


def main():
    """Run all database tests."""
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE CONNECTION TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    results = {}
    
    results["environment"] = test_environment_variables()
    if not results["environment"]:
        logger.error("\n❌ Environment variables not set. Cannot continue.")
        sys.exit(1)
    
    results["connection_string"] = test_connection_string()
    
    results["supabase_client"] = test_supabase_connection()
    
    results["table_access"] = test_sqlalchemy_connection()
    
    results["tables"] = test_tables_exist()
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name.upper():.<30} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

