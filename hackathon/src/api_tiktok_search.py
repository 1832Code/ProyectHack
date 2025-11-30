"""
FastAPI REST API for TikTok Search Service
Author: Mauricio J. @synaw_w
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from apify_client import ApifyClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TikTok Search API",
    description="API para buscar contenido de TikTok usando Apify",
    version="1.0.0"
)


class TikTokSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados")
    use_cache: bool = Field(default=True, description="Usar caché si está disponible")
    force_refresh: bool = Field(default=False, description="Forzar actualización ignorando caché")


class TikTokHashtagRequest(BaseModel):
    hashtag: str = Field(..., description="Hashtag a buscar (sin #)", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class TikTokUserRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario de TikTok (sin @)", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class TikTokSearchResponse(BaseModel):
    status: str
    query: str
    results_count: int
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


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


def search_tiktok(
    client: ApifyClient,
    query: str,
    max_items: int = 30,
    search_type: str = "search",
    use_cache: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Search TikTok content using Apify actor clockworks/tiktok-scraper.
    
    Args:
        client: Apify client instance
        query: Search query (hashtag, username, or search term)
        max_items: Maximum number of results
        search_type: Type of search - "search", "hashtag", or "user"
        use_cache: Whether to use cache if available
        force_refresh: Force refresh ignoring cache
        
    Returns:
        Dict containing search results
    """
    results = {
        "query": query,
        "search_type": search_type,
        "results": []
    }
    
    try:
        logger.info(f"Starting TikTok search for: {query} (type: {search_type}, max_items: {max_items})")
        
        run_input = {
            "resultsPerPage": min(max_items, 100),
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "shouldDownloadSlideshowImages": False
        }
        
        if search_type == "hashtag":
            run_input["hashtags"] = [query.replace("#", "")]
        elif search_type == "user":
            run_input["usernames"] = [query.replace("@", "")]
        else:
            run_input["searchTerms"] = [query]
        
        run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
        
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        results["results"] = list(dataset.items)
        
        logger.info(f"Found {len(results['results'])} results for query: {query}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in TikTok search: {e}", exc_info=True)
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "TikTok Search API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/search",
            "hashtag": "/hashtag",
            "user": "/user",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        client = get_client()
        return HealthResponse(
            status="healthy",
            service="TikTok Search API",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/search", response_model=TikTokSearchResponse)
async def search_tiktok_endpoint(request: TikTokSearchRequest):
    """
    Buscar contenido en TikTok por término de búsqueda.
    
    - **query**: Término de búsqueda (requerido)
    - **max_items**: Máximo de resultados (1-100, default: 30)
    - **use_cache**: Usar caché si está disponible (default: True)
    - **force_refresh**: Forzar actualización ignorando caché (default: False)
    """
    try:
        logger.info(f"TikTok search request: query={request.query}, max_items={request.max_items}")
        
        client = get_client()
        
        results = search_tiktok(
            client=client,
            query=request.query,
            max_items=request.max_items,
            search_type="search",
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        return TikTokSearchResponse(
            status="success",
            query=request.query,
            results_count=len(results["results"]),
            results=results["results"]
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in TikTok search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/hashtag", response_model=TikTokSearchResponse)
async def search_tiktok_hashtag(request: TikTokHashtagRequest):
    """
    Buscar contenido en TikTok por hashtag.
    
    - **hashtag**: Hashtag a buscar sin # (requerido)
    - **max_items**: Máximo de resultados (1-100, default: 30)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"TikTok hashtag search request: hashtag={request.hashtag}, max_items={request.max_items}")
        
        client = get_client()
        
        hashtag = request.hashtag.replace("#", "").strip()
        if not hashtag:
            raise HTTPException(status_code=400, detail="Hashtag no puede estar vacío")
        
        results = search_tiktok(
            client=client,
            query=hashtag,
            max_items=request.max_items,
            search_type="hashtag",
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        return TikTokSearchResponse(
            status="success",
            query=f"#{hashtag}",
            results_count=len(results["results"]),
            results=results["results"]
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in TikTok hashtag search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/user", response_model=TikTokSearchResponse)
async def search_tiktok_user(request: TikTokUserRequest):
    """
    Buscar contenido de un usuario específico en TikTok.
    
    - **username**: Nombre de usuario sin @ (requerido)
    - **max_items**: Máximo de resultados (1-100, default: 30)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"TikTok user search request: username={request.username}, max_items={request.max_items}")
        
        client = get_client()
        
        username = request.username.replace("@", "").strip()
        if not username:
            raise HTTPException(status_code=400, detail="Username no puede estar vacío")
        
        results = search_tiktok(
            client=client,
            query=username,
            max_items=request.max_items,
            search_type="user",
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        return TikTokSearchResponse(
            status="success",
            query=f"@{username}",
            results_count=len(results["results"]),
            results=results["results"]
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in TikTok user search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

