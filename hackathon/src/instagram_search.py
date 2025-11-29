"""
Script to search Instagram content using Apify
Author: Mauricio J. @synaw_w
"""

from apify_client import ApifyClient
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

try:
    env_path = Path(".env")
    if env_path.exists():
        try:
            load_dotenv(env_path, encoding="utf-8")
        except UnicodeDecodeError:
            with open(env_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
            load_dotenv(env_path, encoding="utf-8")
    else:
        load_dotenv()
except Exception as e:
    import sys
    if os.getenv("DEBUG"):
        print(f"Warning: Could not load .env file: {e}", file=sys.stderr)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_apify_client() -> ApifyClient:
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        env_path = Path(".env")
        error_msg = "APIFY_API_TOKEN not found in environment variables"
        if env_path.exists():
            error_msg += f"\n.env file exists at {env_path.absolute()}, but token was not loaded."
            error_msg += "\nPlease check that the file contains: APIFY_API_TOKEN=your_token_here"
        else:
            error_msg += f"\n.env file not found at {Path.cwd() / '.env'}"
            error_msg += "\nPlease create a .env file with: APIFY_API_TOKEN=your_token_here"
        raise ValueError(error_msg)
    return ApifyClient(token)


def get_cache_filename(term: str) -> Path:
    clean_term = term.replace(" ", "_").lower()
    return DATA_DIR / f"instagram_{clean_term}.json"


def save_results_to_json(term: str, results: List[Dict[str, Any]]) -> None:
    cache_file = get_cache_filename(term)
    data = {
        "search_term": term,
        "results_count": len(results),
        "results": results
    }
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {cache_file}")


def load_results_from_json(term: str) -> Optional[List[Dict[str, Any]]]:
    cache_file = get_cache_filename(term)
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {data['results_count']} results from cache: {cache_file}")
        return data.get("results", [])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error loading cache file: {e}")
        return None


def search_instagram_hashtag(client: ApifyClient, hashtag: str, limit: int = 30, use_cache: bool = True, force_refresh: bool = False) -> List[Dict[str, Any]]:
    if use_cache and not force_refresh:
        cached_results = load_results_from_json(hashtag)
        if cached_results is not None:
            return cached_results
    
    run_input = {
        "hashtags": [hashtag],
        "resultsLimit": limit,
    }
    
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    if use_cache:
        save_results_to_json(hashtag, results)
    
    return results


def search_instagram_profile(client: ApifyClient, username: str, limit: int = 30, use_cache: bool = True, force_refresh: bool = False) -> List[Dict[str, Any]]:
    cache_key = f"profile_{username}"
    
    if use_cache and not force_refresh:
        cached_results = load_results_from_json(cache_key)
        if cached_results is not None:
            return cached_results
    
    run_input = {
        "usernames": [username],
        "resultsLimit": limit,
    }
    
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    if use_cache:
        save_results_to_json(cache_key, results)
    
    return results


def search_instagram_term(
    client: ApifyClient, 
    term: str, 
    limit: int = 200, 
    results_type: str = "comments",
    search_limit: int = 4,
    use_cache: bool = True, 
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    if use_cache and not force_refresh:
        cached_results = load_results_from_json(term)
        if cached_results is not None:
            return cached_results
    
    run_input = {
        "addParentData": False,
        "enhanceUserSearchWithFacebookPage": False,
        "isUserReelFeedURL": False,
        "isUserTaggedFeedURL": False,
        "resultsLimit": limit,
        "resultsType": results_type,
        "search": term,
        "searchLimit": search_limit
    }
    
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    if use_cache:
        save_results_to_json(term, results)
    
    return results


def display_results(results: List[Dict[str, Any]]) -> None:
    print(f"\nFound {len(results)} results:\n")
    for idx, item in enumerate(results, 1):
        print(f"--- Result {idx} ---")
        if "text" in item:
            print(f"Text: {item['text'][:100]}...")
        if "ownerUsername" in item:
            print(f"User: {item['ownerUsername']}")
        if "url" in item:
            print(f"URL: {item['url']}")
        if "timestamp" in item:
            print(f"Date: {item['timestamp']}")
        print()

