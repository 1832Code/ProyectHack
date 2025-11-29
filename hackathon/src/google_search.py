"""
Script to search Google using Apify
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


def get_cache_filename(query: str) -> Path:
    clean_query = query.replace(" ", "_").lower()
    # Limitar longitud del nombre de archivo
    if len(clean_query) > 100:
        clean_query = clean_query[:100]
    return DATA_DIR / f"google_search_{clean_query}.json"


def save_results_to_json(query: str, results: List[Dict[str, Any]]) -> None:
    cache_file = get_cache_filename(query)
    data = {
        "search_query": query,
        "results_count": len(results),
        "results": results
    }
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {cache_file}")


def load_results_from_json(query: str) -> Optional[List[Dict[str, Any]]]:
    cache_file = get_cache_filename(query)
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


def search_google(
    client: ApifyClient,
    query: str,
    max_items: int = 100,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    results_per_page: int = 10,
    use_cache: bool = True,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Google using Apify's google-search-scraper actor.
    
    Args:
        client: ApifyClient instance
        query: Search query string
        max_items: Maximum number of results to extract
        country_code: Country code for Google domain (e.g., 'US', 'PE', 'ES')
        language_code: Language code for search results (e.g., 'en', 'es')
        results_per_page: Number of results per page (10, 20, 30, 40, 50, 100)
        use_cache: Whether to use cached results if available
        force_refresh: Force refresh even if cache exists
    
    Returns:
        List of search results
    """
    if use_cache and not force_refresh:
        cached_results = load_results_from_json(query)
        if cached_results is not None:
            return cached_results
    
    run_input = {
        "queries": [query],
        "maxItems": max_items,
        "resultsPerPage": results_per_page,
    }
    
    # Add optional parameters if provided
    if country_code:
        run_input["countryCode"] = country_code
    
    if language_code:
        run_input["languageCode"] = language_code
    
    print(f"Running Google search for: '{query}'")
    print(f"Max items: {max_items}, Results per page: {results_per_page}")
    
    run = client.actor("apify/google-search-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    if use_cache:
        save_results_to_json(query, results)
    
    return results


def search_google_multiple_queries(
    client: ApifyClient,
    queries: List[str],
    max_items: int = 100,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    results_per_page: int = 10,
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search Google for multiple queries.
    
    Args:
        client: ApifyClient instance
        queries: List of search query strings
        max_items: Maximum number of results per query
        country_code: Country code for Google domain
        language_code: Language code for search results
        results_per_page: Number of results per page
        use_cache: Whether to use cached results if available
        force_refresh: Force refresh even if cache exists
    
    Returns:
        Dictionary mapping query to results
    """
    all_results = {}
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Searching for: '{query}'")
        print(f"{'='*60}")
        
        results = search_google(
            client=client,
            query=query,
            max_items=max_items,
            country_code=country_code,
            language_code=language_code,
            results_per_page=results_per_page,
            use_cache=use_cache,
            force_refresh=force_refresh
        )
        
        all_results[query] = results
    
    return all_results


def display_results(results: List[Dict[str, Any]]) -> None:
    """Display Google search results in a readable format."""
    print(f"\n{'='*60}")
    print(f"Found {len(results)} results:")
    print(f"{'='*60}\n")
    
    for idx, item in enumerate(results, 1):
        print(f"--- Result {idx} ---")
        
        # Title
        if "title" in item:
            print(f"Title: {item['title']}")
        elif "name" in item:
            print(f"Title: {item['name']}")
        
        # URL
        if "url" in item:
            print(f"URL: {item['url']}")
        elif "link" in item:
            print(f"URL: {item['link']}")
        
        # Description/Snippet
        if "description" in item:
            desc = item['description']
            if len(desc) > 200:
                desc = desc[:200] + "..."
            print(f"Description: {desc}")
        elif "snippet" in item:
            snippet = item['snippet']
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            print(f"Snippet: {snippet}")
        
        # Position/Rank
        if "position" in item:
            print(f"Position: {item['position']}")
        elif "rank" in item:
            print(f"Rank: {item['rank']}")
        
        # Additional metadata
        if "organicResults" in item:
            print(f"Organic Results: {len(item['organicResults'])}")
        
        print()


def display_results_summary(results: List[Dict[str, Any]]) -> None:
    """Display a summary of Google search results."""
    print(f"\n{'='*60}")
    print(f"Search Results Summary")
    print(f"{'='*60}")
    print(f"Total results: {len(results)}\n")
    
    if not results:
        print("No results found.")
        return
    
    # Show top 10 results
    top_results = results[:10]
    print("Top 10 results:")
    print("-" * 60)
    
    for idx, item in enumerate(top_results, 1):
        title = item.get("title") or item.get("name", "No title")
        url = item.get("url") or item.get("link", "No URL")
        
        # Truncate if too long
        if len(title) > 60:
            title = title[:57] + "..."
        if len(url) > 60:
            url = url[:57] + "..."
        
        print(f"{idx:2d}. {title}")
        print(f"    {url}")
        print()

