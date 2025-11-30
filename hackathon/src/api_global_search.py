"""
FastAPI REST API for Global Search Service
Author: Mauricio J. @synaw_w
"""

from fastapi import FastAPI, HTTPException
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from modules.tiktok_search import search_tiktok
    from modules.google_search import search_google
    from modules.instagram_search import search_instagram_term, search_instagram_hashtag, search_instagram_profile
    from modules.capture import capture_all
    from modules.latest import process_latest_metas, get_posts
    logger.info("✅ All modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import modules: {e}", exc_info=True)
    raise

app = FastAPI(
    title="Global Search API",
    description="API unificada para buscar en Google, Instagram y TikTok",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info("🚀 Starting Global Search API...")
    logger.info(f"PORT: {os.getenv('PORT', '8080')}")
    logger.info(f"APIFY_API_TOKEN: {'✅ set' if os.getenv('APIFY_API_TOKEN') else '❌ not set'}")
    logger.info(f"SUPABASE_URL: {'✅ set' if os.getenv('SUPABASE_URL') else '❌ not set'}")
    logger.info(f"SUPABASE_KEY: {'✅ set' if os.getenv('SUPABASE_KEY') else '❌ not set'}")
    logger.info("✅ Global Search API started successfully")


class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=50, ge=1, le=100, description="Máximo de resultados")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    language_code: Optional[str] = Field(default=None, description="Código de idioma")
    results_per_page: int = Field(default=10, ge=10, le=100, description="Resultados por página")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class InstagramSearchRequest(BaseModel):
    term: Optional[str] = Field(default=None, description="Término de búsqueda")
    hashtag: Optional[str] = Field(default=None, description="Hashtag (sin #)")
    username: Optional[str] = Field(default=None, description="Nombre de usuario (sin @)")
    limit: int = Field(default=30, ge=1, le=500, description="Límite de resultados")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class TikTokSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados")
    search_type: str = Field(default="search", description="Tipo: search, hashtag, user")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class CaptureRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda para capturar", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados por plataforma")
    platforms: Optional[List[str]] = Field(default=None, description="Plataformas a capturar: tiktok, instagram, google. Si es None, captura todas")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    language_code: Optional[str] = Field(default=None, description="Código de idioma")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")
    process_posts: bool = Field(default=True, description="Procesar y guardar en posts automáticamente")


class SearchResponse(BaseModel):
    status: str
    results_count: int
    results: List[Dict[str, Any]]
    message: Optional[str] = None


class CaptureResponse(BaseModel):
    status: str
    message: str
    captured: Dict[str, Optional[int]] = Field(..., description="Dict con plataformas y sus meta IDs (None si se saltó o falló)")
    posts_created: Optional[int] = None
    skipped_platforms: List[str] = Field(default_factory=list, description="Plataformas que se saltaron porque ya existían")
    posts: List[Dict[str, Any]] = Field(default_factory=list, description="Posts existentes en la base de datos")


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
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_token = os.getenv("APIFY_API_TOKEN")
            except ImportError:
                pass
        
        if not api_token:
            raise ValueError("APIFY_API_TOKEN environment variable is not set")
        _apify_client = ApifyClient(api_token)
    return _apify_client


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        return HealthResponse(
            status="healthy",
            service="Global Search API",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Global Search API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "google": "/google",
            "instagram": "/instagram",
            "tiktok": "/tiktok",
            "posts": "/posts",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Global Search API",
        version="1.0.0"
    )


@app.post("/google", response_model=SearchResponse)
async def search_google_endpoint(request: GoogleSearchRequest):
    """
    Buscar en Google.
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
        
        return SearchResponse(
            status="success",
            results_count=len(results),
            results=results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in Google search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/instagram", response_model=SearchResponse)
async def search_instagram_endpoint(request: InstagramSearchRequest):
    """
    Buscar en Instagram.
    """
    try:
        client = get_client()
        results = []
        
        if request.hashtag:
            logger.info(f"Instagram hashtag search: #{request.hashtag}")
            results = search_instagram_hashtag(
                client=client,
                hashtag=request.hashtag,
                limit=request.limit,
                use_cache=request.use_cache,
                force_refresh=request.force_refresh
            )
        elif request.username:
            logger.info(f"Instagram profile search: @{request.username}")
            results = search_instagram_profile(
                client=client,
                username=request.username,
                limit=request.limit,
                use_cache=request.use_cache,
                force_refresh=request.force_refresh
            )
        elif request.term:
            logger.info(f"Instagram term search: {request.term}")
            results = search_instagram_term(
                client=client,
                term=request.term,
                limit=request.limit,
                use_cache=request.use_cache,
                force_refresh=request.force_refresh
            )
        else:
            raise HTTPException(status_code=400, detail="Debe proporcionar term, hashtag o username")
        
        return SearchResponse(
            status="success",
            results_count=len(results),
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Instagram search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/tiktok", response_model=SearchResponse)
async def search_tiktok_endpoint(request: TikTokSearchRequest):
    """
    Buscar en TikTok.
    """
    try:
        logger.info(f"TikTok search request: query={request.query}, type={request.search_type}")
        
        client = get_client()
        
        results_dict = search_tiktok(
            client=client,
            query=request.query,
            max_items=request.max_items,
            search_type=request.search_type,
            country_code=request.country_code,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh
        )
        
        results = results_dict.get("results", [])
        
        return SearchResponse(
            status="success",
            results_count=len(results),
            results=results
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in TikTok search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.get("/post/local", response_model=Dict[str, Any])
async def get_local_posts(limit: int = 100, id_company: int = 1):
    """
    Obtener todos los posts de la base de datos.
    
    Args:
        limit: Número máximo de posts a retornar (default: 100)
        id_company: ID de la compañía (default: 1)
        
    Returns:
        Dict con status y lista de posts
    """
    try:
        logger.info(f"Getting local posts (company: {id_company}, limit: {limit})")
        
        posts = get_posts(id_company=id_company, limit=limit)
        
        return {
            "status": "success",
            "count": len(posts),
            "posts": posts
        }
        
    except Exception as e:
        logger.error(f"Error getting local posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/posts", response_model=CaptureResponse)
async def posts_endpoint(request: CaptureRequest):
    """
    Capturar datos de todas las plataformas (TikTok, Instagram, Google) para una query.
    Solo guarda si la query no existe previamente en cada plataforma.
    Opcionalmente procesa y guarda en posts.
    """
    try:
        logger.info(f"Capture request: query={request.query}, platforms={request.platforms}")
        
        client = get_client()
        
        captured = capture_all(
            client=client,
            query=request.query,
            platforms=request.platforms,
            max_items=request.max_items,
            country_code=request.country_code,
            language_code=request.language_code,
            use_cache=request.use_cache,
            force_refresh=request.force_refresh,
            skip_existing=True
        )
        
        skipped_platforms = [platform for platform, meta_id in captured.items() if meta_id is None]
        successful_platforms = [platform for platform, meta_id in captured.items() if meta_id is not None]
        
        logger.info("Retrieving posts from database...")
        posts = get_posts(id_company=1, limit=100)
        logger.info(f"Found {len(posts)} posts in database")
        
        if not successful_platforms:
            return CaptureResponse(
                status="success",
                message=f"Query '{request.query}' procesada. No se encontraron resultados nuevos en ninguna plataforma.",
                captured=captured,
                skipped_platforms=skipped_platforms,
                posts=posts
            )
        
        posts_created = 0
        if request.process_posts:
            logger.info(f"Processing latest metas for query: {request.query}")
            for platform in successful_platforms:
                post_ids = process_latest_metas(
                    id_company=1,
                    label=platform,
                    limit=1
                )
                posts_created += len(post_ids)
            logger.info(f"Created {posts_created} posts from captured data")
        
        logger.info("Retrieving posts from database...")
        posts = get_posts(id_company=1, limit=100)
        logger.info(f"Found {len(posts)} posts in database")
        
        message = f"Datos capturados exitosamente en {len(successful_platforms)} plataforma(s): {', '.join(successful_platforms)}"
        if skipped_platforms:
            message += f". Saltadas: {', '.join(skipped_platforms)}"
        
        return CaptureResponse(
            status="success",
            message=message,
            captured=captured,
            posts_created=posts_created if request.process_posts else None,
            skipped_platforms=skipped_platforms,
            posts=posts
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in capture: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_global_search:app",
        host=host,
        port=port,
        log_level="info"
    )

