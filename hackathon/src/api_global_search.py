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

from src.modules.tiktok_search import search_tiktok
from src.modules.google_search import search_google
from src.modules.x_search import search_x
from src.modules.instagram_search import search_instagram_term, search_instagram_hashtag, search_instagram_profile
from src.modules.capture import capture_all
from src.modules.latest import process_latest_metas, get_posts
from src.modules.analytics import count_keyword_mentions, calculate_sentiment_approval, get_keywords
from src.modules.analytics_opportunity import get_business_opportunity

app = FastAPI(
    title="Global Search API",
    description="API unificada para buscar en Google, Instagram, TikTok y X (Twitter)",
    version="1.0.0"
)


class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=50, ge=1, le=100, description="Máximo de resultados")
    country_code: Optional[str] = Field(default=None, description="Código de país")
    language_code: Optional[str] = Field(default=None, description="Código de idioma")
    results_per_page: int = Field(default=100, ge=10, le=100, description="Resultados por página")
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


class XSearchRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda", min_length=1)
    max_items: int = Field(default=1000, ge=1, le=1000, description="Máximo de resultados")
    geocode: Optional[str] = Field(default=None, description="Geocode en formato 'latitude,longitude,radius' (ej: '-12.0257733,-77.3174516,20km')")
    sort: str = Field(default="Latest", description="Orden: Latest, Top, People, Photos, Videos")
    tweet_language: str = Field(default="es", description="Código de idioma para tweets")
    use_cache: bool = Field(default=True, description="Usar caché")
    force_refresh: bool = Field(default=False, description="Forzar actualización")


class CaptureRequest(BaseModel):
    query: str = Field(..., description="Término de búsqueda para capturar", min_length=1)
    max_items: int = Field(default=30, ge=1, le=100, description="Máximo de resultados por plataforma")
    platforms: Optional[List[str]] = Field(default=None, description="Plataformas a capturar: tiktok, instagram, google, x. Si es None, captura todas")
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


class KeywordMentionsResponse(BaseModel):
    keyword: str
    count_mentions: int
    error: Optional[str] = None


class SentimentApprovalResponse(BaseModel):
    approval_score: float
    total_posts: int
    positive_count: int
    negative_count: int
    neutral_count: int
    keyword: Optional[str] = None
    error: Optional[str] = None


class KeywordsResponse(BaseModel):
    query: str
    keywords: List[Dict[str, Any]]
    error: Optional[str] = None


class OpportunityRequest(BaseModel):
    query: str = Field(..., description="Query para filtrar posts", min_length=1)
    id_company: int = Field(default=1, description="ID de la compañía")
    limit: int = Field(default=100, ge=1, le=200, description="Número máximo de posts a analizar")


class BusinessOpportunityItem(BaseModel):
    insight: str = Field(..., description="Texto corto de lo que se encontró en redes sociales")
    ideas: List[str] = Field(..., description="Array con 1 a 3 ideas de cómo aprovechar la oportunidad")
    posts: List[Dict[str, Any]] = Field(default_factory=list, description="Array con los objetos completos de posts de la base de datos que respaldan la oportunidad")


class OpportunityResponse(BaseModel):
    query: str
    results: List[BusinessOpportunityItem] = Field(default_factory=list, description="Array con 1 a 5 oportunidades de negocio segmentadas")
    error: Optional[str] = None


class AnalyticsResponse(BaseModel):
    keyword: str
    count_mentions: int
    approval_score: float
    sentiment_total_posts: int
    sentiment_positive_count: int
    sentiment_negative_count: int
    sentiment_neutral_count: int
    keywords: List[str] = Field(default_factory=list, description="Top 5 tópicos de marketing generados por agente DeepSeek")
    error: Optional[str] = None


class KeywordsResponse(BaseModel):
    query: str
    keywords: List[Dict[str, Any]]
    error: Optional[str] = None


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
            "x": "/x",
            "posts": "/posts",
            "analytics": "/analytics",
            "oportunity": "/oportunity",
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


@app.post("/x", response_model=SearchResponse)
async def search_x_endpoint(request: XSearchRequest):
    """
    Buscar en X (Twitter).
    """
    try:
        logger.info(f"X search request: query={request.query}, geocode={request.geocode}, sort={request.sort}")
        
        client = get_client()
        
        results_dict = search_x(
            client=client,
            query=request.query,
            max_items=request.max_items,
            geocode=request.geocode,
            sort=request.sort,
            tweet_language=request.tweet_language,
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
        logger.error(f"Error in X search: {e}", exc_info=True)
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
        logger.info(f"🔍 GET /post/local - company: {id_company}, limit: {limit}")
        logger.info(f"SUPABASE_URL: {'✅ set' if os.getenv('SUPABASE_URL') else '❌ not set'}")
        logger.info(f"SUPABASE_KEY: {'✅ set' if os.getenv('SUPABASE_KEY') else '❌ not set'}")
        
        posts = get_posts(id_company=id_company, limit=limit)
        
        logger.info(f"✅ Retrieved {len(posts)} posts from database")
        
        response = {
            "status": "success",
            "count": len(posts),
            "posts": posts
        }
        
        logger.info(f"📤 Returning response with {len(posts)} posts")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error getting local posts: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(keyword: str, id_company: int = 1, limit: int = 1000):
    """
    Obtener todas las métricas de analytics para uno o múltiples keywords.
    Si se proporcionan múltiples keywords separados por comas, se combinan los resultados.
    Incluye: count_mentions y sentiment approval.
    
    Args:
        keyword: Keyword(s) a analizar (requerido). Puede ser uno o múltiples separados por comas (ej: "pollo,arroz,ceviche")
        id_company: ID de la compañía (default: 1)
        limit: Número máximo de posts a analizar para sentiment (default: 1000)
        
    Returns:
        Dict con todas las métricas combinadas: count_mentions, approval_score, sentiment_total_posts, etc.
    """
    try:
        logger.info(f"Analytics request: keyword='{keyword}', id_company={id_company}, limit={limit}")
        
        keywords_list = [k.strip() for k in keyword.split(",") if k.strip()]
        
        if not keywords_list:
            raise HTTPException(status_code=400, detail="Al menos un keyword es requerido")
        
        logger.info(f"Processing {len(keywords_list)} keywords: {keywords_list}")
        
        total_mentions = 0
        all_sentiment_scores = []
        total_sentiment_posts = 0
        total_positive = 0
        total_negative = 0
        total_neutral = 0
        errors = []
        
        for kw in keywords_list:
            try:
                mentions_result = count_keyword_mentions(keyword=kw, id_company=id_company)
                sentiment_result = calculate_sentiment_approval(keyword=kw, id_company=id_company, limit=limit)
                
                total_mentions += mentions_result.get("count_mentions", 0)
                
                approval_score = sentiment_result.get("approval_score", 0)
                sentiment_posts = sentiment_result.get("total_posts", 0)
                
                if sentiment_posts > 0:
                    all_sentiment_scores.append(approval_score)
                    total_sentiment_posts += sentiment_posts
                    total_positive += sentiment_result.get("positive_count", 0)
                    total_negative += sentiment_result.get("negative_count", 0)
                    total_neutral += sentiment_result.get("neutral_count", 0)
                
                if mentions_result.get("error"):
                    errors.append(f"{kw}: {mentions_result.get('error')}")
                if sentiment_result.get("error"):
                    errors.append(f"{kw}: {sentiment_result.get('error')}")
                    
            except Exception as e:
                logger.warning(f"Error processing keyword '{kw}': {e}")
                errors.append(f"{kw}: {str(e)}")
        
        combined_approval_score = sum(all_sentiment_scores) / len(all_sentiment_scores) if all_sentiment_scores else 0
        
        combined_keyword = ", ".join(keywords_list)
        
        keywords_result = get_keywords(query=combined_keyword, id_company=id_company, limit=limit)
        extracted_keywords = keywords_result.get("keywords", [])
        
        return AnalyticsResponse(
            keyword=combined_keyword,
            count_mentions=total_mentions,
            approval_score=round(combined_approval_score, 2),
            sentiment_total_posts=total_sentiment_posts,
            sentiment_positive_count=total_positive,
            sentiment_negative_count=total_negative,
            sentiment_neutral_count=total_neutral,
            keywords=extracted_keywords,
            error="; ".join(errors) if errors else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.post("/oportunity", response_model=OpportunityResponse)
async def opportunity_endpoint(request: OpportunityRequest):
    """
    Generar oportunidades de negocio basadas en posts relacionados con una query.
    Usa un agente DeepSeek iterativo (2 pasos) para analizar posts y generar entre 1 y 5 oportunidades segmentadas.
    
    Args:
        query: Query para filtrar posts (requerido)
        id_company: ID de la compañía (default: 1)
        limit: Número máximo de posts a analizar (default: 100, máximo: 200)
        
    Returns:
        Dict con results (array de 1 a 5 oportunidades), cada una con:
        - insight: texto corto de lo encontrado en redes
        - ideas: array de 1 a 3 ideas para aprovechar la oportunidad
        - posts: array de IDs de posts de la base de datos que respaldan la oportunidad
    """
    try:
        logger.info(f"Opportunity request: query='{request.query}', id_company={request.id_company}, limit={request.limit}")
        
        result = get_business_opportunity(
            query=request.query,
            id_company=request.id_company,
            limit=request.limit
        )
        
        results = result.get("results", [])
        
        return OpportunityResponse(
            query=result.get("query", request.query),
            results=results,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in opportunity endpoint: {e}", exc_info=True)
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
        posts = []
        if successful_platforms:
            for platform in successful_platforms:
                platform_posts = get_posts(id_company=1, limit=100, source=platform, query=request.query)
                posts.extend(platform_posts)
        else:
            posts = get_posts(id_company=1, limit=100, query=request.query)
        
        logger.info(f"Found {len(posts)} posts in database for query '{request.query}' and platforms {successful_platforms}")
        
        if not successful_platforms:
            return CaptureResponse(
                status="success",
                message=f"Query '{request.query}' procesada. No se encontraron resultados nuevos en ninguna plataforma.",
                captured=captured,
                skipped_platforms=skipped_platforms,
                posts=posts
            )
        
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

