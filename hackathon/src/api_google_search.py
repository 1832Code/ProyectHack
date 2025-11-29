"""
FastAPI REST API for Google Search Service
Author: Mauricio J. @synaw_w
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from google_search import (
    get_apify_client,
    search_google,
    search_google_multiple_queries
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Google Search API",
    description="API para buscar en Google usando Apify",
    version="1.0.0"
)


# Request Models
class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=50, ge=1, le=100, description="Máximo de resultados")
    country_code: Optional[str] = Field(default=None, description="Código de país (ej: 'PE', 'US', 'ES')")
    language_code: Optional[str] = Field(default=None, description="Código de idioma (ej: 'es', 'en')")
    results_per_page: int = Field(default=10, ge=10, le=100, description="Resultados por página (10, 20, 30, 40, 50, 100)")
    use_cache: bool = Field(default=True, description="Usar caché si está disponible")
    force_refresh: bool = Field(default=False, description="Forzar actualización ignorando caché")


class GoogleSearchMultipleRequest(BaseModel):
    queries: List[str] = Field(..., description="Lista de términos de búsqueda", min_items=1)
    max_items: int = Field(default=50, ge=1, le=100, description="Máximo de resultados por query")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    language_code: Optional[str] = Field(default=None, description="Código de idioma")
    results_per_page: int = Field(default=10, ge=10, le=100, description="Resultados por página")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


# Response Models
class GoogleSearchResponse(BaseModel):
    status: str
    query: str
    results_count: int
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class GoogleSearchMultipleResponse(BaseModel):
    status: str
    queries: List[str]
    results: Dict[str, List[Dict[str, Any]]]
    total_results: int
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
        "service": "Google Search API",
        "version": "1.0.0",
        "description": "API para buscar en Google usando Apify",
        "endpoints": {
            "POST /search": "Buscar en Google",
            "POST /search/multiple": "Búsqueda múltiple",
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
            "service": "Google Search API",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/search", response_model=GoogleSearchResponse)
async def search_google_endpoint(request: GoogleSearchRequest):
    """
    Buscar en Google.
    
    - **query**: Término de búsqueda (requerido)
    - **max_items**: Máximo de resultados (1-100, default: 50)
    - **country_code**: Código de país (opcional)
    - **language_code**: Código de idioma (opcional)
    - **results_per_page**: Resultados por página (10, 20, 30, 40, 50, 100, default: 10)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"Google search request: query={request.query}")
        
        client = get_client()
        
        results = search_google(
            client=client,
            query=request.query,
            max_items=request.max_items,
            country_code=request.country_code,
            language_code=request.language_code,
            results_per_page=request.results_per_page,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        logger.info(f"Search completed: query={request.query}, results={len(results)}")
        
        return GoogleSearchResponse(
            status="success",
            query=request.query,
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


@app.post("/search/multiple", response_model=GoogleSearchMultipleResponse)
async def search_google_multiple_endpoint(request: GoogleSearchMultipleRequest):
    """
    Búsqueda múltiple en Google.
    
    - **queries**: Lista de términos de búsqueda (requerido, mínimo 1)
    - **max_items**: Máximo de resultados por query (1-100, default: 50)
    - **country_code**: Código de país (opcional)
    - **language_code**: Código de idioma (opcional)
    - **results_per_page**: Resultados por página (default: 10)
    - **use_cache**: Usar caché (default: True)
    - **force_refresh**: Forzar actualización (default: False)
    """
    try:
        logger.info(f"Multiple Google search request: queries={request.queries}")
        
        client = get_client()
        
        all_results = search_google_multiple_queries(
            client=client,
            queries=request.queries,
            max_items=request.max_items,
            country_code=request.country_code,
            language_code=request.language_code,
            results_per_page=request.results_per_page,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        total_results = sum(len(results) for results in all_results.values())
        
        logger.info(f"Multiple search completed: queries={len(request.queries)}, total_results={total_results}")
        
        return GoogleSearchMultipleResponse(
            status="success",
            queries=request.queries,
            results=all_results,
            total_results=total_results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during multiple search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/search/{query}", response_model=GoogleSearchResponse)
async def search_google_get(
    query: str,
    max_items: int = 50,
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    results_per_page: int = 10,
    use_cache: bool = True,
    force_refresh: bool = False
):
    """Buscar en Google usando GET (conveniencia)."""
    request = GoogleSearchRequest(
        query=query,
        max_items=max_items,
        country_code=country_code,
        language_code=language_code,
        results_per_page=results_per_page,
        use_cache=use_cache,
        force_refresh=force_refresh
    )
    return await search_google_endpoint(request)


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
        "api_google_search:app",
        host=host,
        port=port,
        log_level="info"
    )

