"""
FastAPI REST API for Instagram Search Service
Author: Mauricio J. @synaw_w
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging

try:
    from instagram_search import (
        get_apify_client,
        search_instagram_term,
        search_instagram_hashtag,
        search_instagram_profile
    )
except ImportError:
    logging.warning("instagram_search module not found. Creating stub functions.")
    def get_apify_client():
        raise NotImplementedError("instagram_search module not available")
    def search_instagram_term(*args, **kwargs):
        raise NotImplementedError("instagram_search module not available")
    def search_instagram_hashtag(*args, **kwargs):
        raise NotImplementedError("instagram_search module not available")
    def search_instagram_profile(*args, **kwargs):
        raise NotImplementedError("instagram_search module not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Instagram Search API",
    description="API para buscar contenido de Instagram usando Apify",
    version="1.0.0"
)


# Request Models
class InstagramSearchRequest(BaseModel):
    term: str = Field(..., description="Término de búsqueda", min_length=1)
    limit: int = Field(default=200, ge=1, le=500, description="Límite de resultados")
    results_type: str = Field(default="comments", description="Tipo de resultados: comments, posts, etc.")
    search_limit: int = Field(default=4, ge=1, le=10, description="Límite de búsqueda")
    use_cache: bool = Field(default=True, description="Usar caché si está disponible")
    force_refresh: bool = Field(default=False, description="Forzar actualización ignorando caché")


class InstagramHashtagRequest(BaseModel):
    hashtag: str = Field(..., description="Hashtag a buscar (sin #)", min_length=1)
    limit: int = Field(default=30, ge=1, le=500, description="Límite de resultados")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class InstagramProfileRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario de Instagram", min_length=1)
    limit: int = Field(default=30, ge=1, le=500, description="Límite de resultados")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


# Response Models
class InstagramSearchResponse(BaseModel):
    status: str
    term: str
    results_count: int
    results: List[Dict[str, Any]]
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
        _apify_client = get_apify_client()
    return _apify_client


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Instagram Search API",
        "version": "1.0.0",
        "description": "API para buscar contenido de Instagram usando Apify",
        "endpoints": {
            "POST /search/term": "Buscar por término",
            "POST /search/hashtag": "Buscar por hashtag",
            "POST /search/profile": "Buscar perfil de usuario",
            "GET /health": "Health check",
            "GET /docs": "Documentación interactiva (Swagger UI)",
            "GET /redoc": "Documentación alternativa (ReDoc)"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        client = get_client()
        return {
            "status": "healthy",
            "service": "Instagram Search API",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/search/term", response_model=InstagramSearchResponse)
async def search_instagram_term_endpoint(request: InstagramSearchRequest):
    """
    Buscar en Instagram por término.
    
    - **term**: Término de búsqueda (requerido)
    - **limit**: Límite de resultados (1-500, default: 200)
    - **results_type**: Tipo de resultados (default: "comments")
    - **search_limit**: Límite de búsqueda (1-10, default: 4)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"Instagram term search request: term={request.term}")
        
        client = get_client()
        
        results = search_instagram_term(
            client=client,
            term=request.term,
            limit=request.limit,
            results_type=request.results_type,
            search_limit=request.search_limit,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        logger.info(f"Search completed: term={request.term}, results={len(results)}")
        
        return InstagramSearchResponse(
            status="success",
            term=request.term,
            results_count=len(results),
            results=results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/search/hashtag", response_model=InstagramSearchResponse)
async def search_instagram_hashtag_endpoint(request: InstagramHashtagRequest):
    """
    Buscar en Instagram por hashtag.
    
    - **hashtag**: Hashtag a buscar sin el símbolo # (requerido)
    - **limit**: Límite de resultados (1-500, default: 30)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"Instagram hashtag search request: hashtag={request.hashtag}")
        
        client = get_client()
        
        results = search_instagram_hashtag(
            client=client,
            hashtag=request.hashtag,
            limit=request.limit,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        logger.info(f"Search completed: hashtag={request.hashtag}, results={len(results)}")
        
        return InstagramSearchResponse(
            status="success",
            term=f"#{request.hashtag}",
            results_count=len(results),
            results=results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/search/profile", response_model=InstagramSearchResponse)
async def search_instagram_profile_endpoint(request: InstagramProfileRequest):
    """
    Buscar perfil de usuario en Instagram.
    
    - **username**: Nombre de usuario de Instagram (requerido)
    - **limit**: Límite de resultados (1-500, default: 30)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"Instagram profile search request: username={request.username}")
        
        client = get_client()
        
        results = search_instagram_profile(
            client=client,
            username=request.username,
            limit=request.limit,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        logger.info(f"Search completed: username={request.username}, results={len(results)}")
        
        return InstagramSearchResponse(
            status="success",
            term=f"@{request.username}",
            results_count=len(results),
            results=results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


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
        "api_instagram_search:app",
        host=host,
        port=port,
        log_level="info"
    )

