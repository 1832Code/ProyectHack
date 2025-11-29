"""
FastAPI REST API for Company Lookup Service
Author: Mauricio J. @synaw_w
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from apify_client import ApifyClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Company Lookup API",
    description="API para buscar información de empresas y keywords usando Apify",
    version="1.0.0"
)


# Request Models
class CompanyLookupRequest(BaseModel):
    company: str = Field(..., description="Nombre de la empresa a buscar", min_length=1)
    keywords: Optional[List[str]] = Field(default=None, description="Lista de keywords relacionados")
    max_items_per_query: int = Field(default=50, ge=1, le=100, description="Máximo de resultados por búsqueda")
    country_code: Optional[str] = Field(default=None, description="Código de país (ej: 'PE', 'US', 'ES')")
    language_code: Optional[str] = Field(default=None, description="Código de idioma (ej: 'es', 'en')")
    use_cache: bool = Field(default=True, description="Usar caché si está disponible")
    force_refresh: bool = Field(default=False, description="Forzar actualización ignorando caché")


# Response Models
class CompanyLookupResponse(BaseModel):
    status: str
    company: str
    keywords: List[str]
    results: Dict[str, Any]
    summary: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# Global client (lazy initialization)
_apify_client = None


def get_client():
    """Get or create Apify client (singleton)."""
    global _apify_client
    if _apify_client is None:
        api_token = os.getenv("APIFY_API_TOKEN")
        if not api_token:
            raise ValueError("APIFY_API_TOKEN environment variable is not set")
        _apify_client = ApifyClient(api_token)
    return _apify_client


def lookup_company(
    client: ApifyClient,
    company: str,
    keywords: Optional[List[str]] = None,
    max_items_per_query: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Lookup company information and related keywords using Apify.
    
    Args:
        client: Apify client instance
        company: Company name to search
        keywords: Optional list of related keywords
        max_items_per_query: Maximum items per search query
        country_code: Optional country code filter
        language_code: Optional language code filter
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        Dict containing search results for company and keywords
    """
    results = {
        "company": company,
        "keywords": keywords or [],
        "company_results": [],
        "keyword_results": {}
    }
    
    try:
        logger.info(f"Starting company lookup for: {company}")
        
        run_input = {
            "focusOnPaidAds": False,
            "forceExactMatch": False,
            "includeIcons": False,
            "includeUnfilteredResults": False,
            "maxPagesPerQuery": 1,
            "maximumLeadsEnrichmentRecords": 0,
            "mobileResults": False,
            "queries": company,
            "resultsPerPage": min(max_items_per_query, 100),
            "saveHtml": False,
            "saveHtmlToKeyValueStore": True,
            "aiMode": "aiModeOff",
            "searchLanguage": language_code or "",
            "languageCode": language_code or "",
            "wordsInTitle": [],
            "wordsInText": [],
            "wordsInUrl": []
        }
        
        run = client.actor("apify/google-search-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results["company_results"] = list(dataset.items)
        
        logger.info(f"Found {len(results['company_results'])} results for company: {company}")
        
        if keywords:
            results["keyword_results"] = {}
            for keyword in keywords:
                try:
                    keyword_input = {
                        "focusOnPaidAds": False,
                        "forceExactMatch": False,
                        "includeIcons": False,
                        "includeUnfilteredResults": False,
                        "maxPagesPerQuery": 1,
                        "maximumLeadsEnrichmentRecords": 0,
                        "mobileResults": False,
                        "queries": keyword,
                        "resultsPerPage": min(max_items_per_query, 100),
                        "saveHtml": False,
                        "saveHtmlToKeyValueStore": True,
                        "aiMode": "aiModeOff",
                        "searchLanguage": language_code or "",
                        "languageCode": language_code or "",
                        "wordsInTitle": [],
                        "wordsInText": [],
                        "wordsInUrl": []
                    }
                    
                    keyword_run = client.actor("apify/google-search-scraper").call(run_input=keyword_input)
                    keyword_dataset = client.dataset(keyword_run["defaultDatasetId"]).list_items()
                    results["keyword_results"][keyword] = list(keyword_dataset.items)
                    
                    logger.info(f"Found {len(results['keyword_results'][keyword])} results for keyword: {keyword}")
                except Exception as e:
                    logger.error(f"Error searching keyword '{keyword}': {e}")
                    results["keyword_results"][keyword] = []
        
    except Exception as e:
        logger.error(f"Error in company lookup: {e}")
        raise
    
    return results


def get_summary_stats(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate summary statistics from lookup results.
    
    Args:
        results: Results dictionary from lookup_company
        
    Returns:
        Dict containing summary statistics
    """
    company_results = results.get("company_results", [])
    keyword_results = results.get("keyword_results", {})
    
    total_company_results = len(company_results)
    total_keyword_results = sum(len(items) for items in keyword_results.values())
    
    stats = {
        "total_company_results": total_company_results,
        "total_keyword_results": total_keyword_results,
        "total_results": total_company_results + total_keyword_results,
        "keywords_searched": len(keyword_results),
        "keywords_with_results": sum(1 for items in keyword_results.values() if len(items) > 0)
    }
    
    return stats


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Company Lookup API",
        "version": "1.0.0",
        "description": "API para buscar información de empresas y keywords usando Apify",
        "endpoints": {
            "POST /lookup/company": "Buscar información de una empresa",
            "GET /health": "Health check",
            "GET /docs": "Documentación interactiva (Swagger UI)",
            "GET /redoc": "Documentación alternativa (ReDoc)"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Try to get client to verify configuration
        client = get_client()
        return {
            "status": "healthy",
            "service": "Company Lookup API",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/lookup/company", response_model=CompanyLookupResponse)
async def lookup_company_endpoint(
    request: CompanyLookupRequest,
    background_tasks: BackgroundTasks
):
    """
    Buscar información de una empresa y keywords relacionados.
    
    - **company**: Nombre de la empresa (requerido)
    - **keywords**: Lista opcional de keywords para buscar
    - **max_items_per_query**: Máximo de resultados por búsqueda (1-100, default: 50)
    - **country_code**: Código de país para la búsqueda (opcional)
    - **language_code**: Código de idioma para la búsqueda (opcional)
    - **use_cache**: Usar caché si está disponible (default: True)
    - **force_refresh**: Forzar actualización ignorando caché (default: False)
    """
    try:
        logger.info(f"Company lookup request: company={request.company}, keywords={request.keywords}")
        
        # Get Apify client
        client = get_client()
        
        # Perform lookup
        results = lookup_company(
            client=client,
            company=request.company,
            keywords=request.keywords,
            max_items_per_query=request.max_items_per_query,
            country_code=request.country_code,
            language_code=request.language_code,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        # Get summary statistics
        summary = get_summary_stats(results)
        
        logger.info(f"Lookup completed: company={request.company}, total_results={summary.get('total_company_results', 0) + summary.get('total_keyword_results', 0)}")
        
        return CompanyLookupResponse(
            status="success",
            company=results.get("company", request.company),
            keywords=results.get("keywords", request.keywords or []),
            results=results,
            summary=summary
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Error during company lookup: {error_detail}")
        logger.error(f"Traceback: {error_traceback}")
        
        debug_info = {}
        if os.getenv("DEBUG"):
            debug_info = {
                "traceback": error_traceback,
                "pythonpath": os.getenv("PYTHONPATH", "not set"),
                "cwd": os.getcwd()
            }
        
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {error_detail}. Debug: {debug_info if debug_info else 'Enable DEBUG env var for details'}"
        )


@app.get("/lookup/company/{company_name}", response_model=CompanyLookupResponse)
async def lookup_company_get(
    company_name: str,
    keywords: Optional[str] = None,
    max_items: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    use_cache: bool = True,
    force_refresh: bool = False
):
    """
    Buscar información de una empresa usando GET (conveniencia).
    
    - **company_name**: Nombre de la empresa en la URL
    - **keywords**: Keywords separados por comas (opcional)
    - **max_items**: Máximo de resultados por búsqueda (default: 50)
    - **country_code**: Código de país (opcional)
    - **language_code**: Código de idioma (opcional)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    # Parse keywords from query string
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    # Create request object
    request = CompanyLookupRequest(
        company=company_name,
        keywords=keyword_list,
        max_items_per_query=max_items,
        country_code=country_code,
        language_code=language_code,
        use_cache=use_cache,
        force_refresh=force_refresh
    )
    
    # Use POST endpoint logic
    return await lookup_company_endpoint(request, BackgroundTasks())


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Error interno del servidor",
            "detail": str(exc) if os.getenv("DEBUG") else "Contacte al administrador"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_company_lookup:app",
        host=host,
        port=port,
        log_level="info"
    )

