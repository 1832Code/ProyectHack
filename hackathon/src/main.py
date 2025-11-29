"""
Main entry point for Google Cloud Run
Executes Instagram and Google search using Apify
Author: Mauricio J. @synaw_w
"""

import os
from instagram_search import (
    get_apify_client as get_instagram_client,
    search_instagram_term,
    display_results as display_instagram_results
)
from google_search import (
    get_apify_client as get_google_client,
    search_google,
    display_results as display_google_results,
    display_results_summary
)


def run_instagram_search():
    """Run Instagram search example."""
    client = get_instagram_client()
    
    search_term = "pollo a la brasa"
    
    print(f"Searching for '{search_term}' on Instagram...")
    
    try:
        results = search_instagram_term(
            client, 
            search_term, 
            limit=200,
            results_type="comments",
            search_limit=4
        )
        display_instagram_results(results)
        return {"status": "success", "results_count": len(results)}
    except Exception as e:
        error_msg = f"Error during Instagram search: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def run_google_search():
    """Run Google search example."""
    client = get_google_client()
    
    search_query = "pollo a la brasa peru"
    
    print(f"Searching for '{search_query}' on Google...")
    
    try:
        results = search_google(
            client,
            query=search_query,
            max_items=50,
            country_code="PE",  # Peru
            language_code="es",  # Spanish
            results_per_page=10
        )
        display_results_summary(results)
        return {"status": "success", "results_count": len(results)}
    except Exception as e:
        error_msg = f"Error during Google search: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def main():
    """Main function - runs both searches or based on environment variable."""
    search_type = os.getenv("SEARCH_TYPE", "google").lower()
    
    if search_type == "instagram":
        return run_instagram_search()
    elif search_type == "google":
        return run_google_search()
    elif search_type == "both":
        print("=" * 60)
        print("Running Instagram Search")
        print("=" * 60)
        instagram_result = run_instagram_search()
        
        print("\n" + "=" * 60)
        print("Running Google Search")
        print("=" * 60)
        google_result = run_google_search()
        
        return {
            "instagram": instagram_result,
            "google": google_result
        }
    else:
        print(f"Unknown search type: {search_type}")
        print("Available types: 'instagram', 'google', 'both'")
        print("Defaulting to Google search...")
        return run_google_search()


if __name__ == "__main__":
    main()

