"""
Example script showing how to use Google Search functionality
Author: Mauricio J. @synaw_w
"""

from google_search import (
    get_apify_client,
    search_google,
    search_google_multiple_queries,
    display_results,
    display_results_summary
)


def example_single_search():
    """Example: Single Google search."""
    print("=" * 60)
    print("Example 1: Single Google Search")
    print("=" * 60)
    
    client = get_apify_client()
    
    results = search_google(
        client=client,
        query="pollo a la brasa peru",
        max_items=20,
        country_code="PE",  # Peru
        language_code="es",  # Spanish
        results_per_page=10
    )
    
    display_results_summary(results)


def example_multiple_searches():
    """Example: Multiple Google searches."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Google Searches")
    print("=" * 60)
    
    client = get_apify_client()
    
    queries = [
        "pollo a la brasa",
        "restaurantes peruanos",
        "comida peruana"
    ]
    
    all_results = search_google_multiple_queries(
        client=client,
        queries=queries,
        max_items=10,
        country_code="PE",
        language_code="es"
    )
    
    for query, results in all_results.items():
        print(f"\nQuery: '{query}' - Found {len(results)} results")


def example_detailed_results():
    """Example: Display detailed results."""
    print("\n" + "=" * 60)
    print("Example 3: Detailed Results Display")
    print("=" * 60)
    
    client = get_apify_client()
    
    results = search_google(
        client=client,
        query="pollo a la brasa receta",
        max_items=5,
        country_code="PE",
        language_code="es"
    )
    
    display_results(results)


def example_with_cache():
    """Example: Using cache to avoid repeated API calls."""
    print("\n" + "=" * 60)
    print("Example 4: Using Cache")
    print("=" * 60)
    
    client = get_apify_client()
    
    query = "pollo a la brasa"
    
    # First call - will fetch from API
    print("First call (fetching from API)...")
    results1 = search_google(
        client=client,
        query=query,
        max_items=10,
        use_cache=True
    )
    print(f"Got {len(results1)} results\n")
    
    # Second call - will use cache
    print("Second call (using cache)...")
    results2 = search_google(
        client=client,
        query=query,
        max_items=10,
        use_cache=True,
        force_refresh=False  # Use cache
    )
    print(f"Got {len(results2)} results (from cache)\n")
    
    # Third call - force refresh
    print("Third call (force refresh)...")
    results3 = search_google(
        client=client,
        query=query,
        max_items=10,
        use_cache=True,
        force_refresh=True  # Force refresh
    )
    print(f"Got {len(results3)} results (fresh from API)")


if __name__ == "__main__":
    # Run examples
    try:
        example_single_search()
        example_multiple_searches()
        example_detailed_results()
        example_with_cache()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

