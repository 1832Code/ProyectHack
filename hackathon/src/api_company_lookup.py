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
import json
import hashlib
from functools import lru_cache
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timedelta
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

try:
    import langchain
    logger.info(f"LangChain base package version: {langchain.__version__}")
    from langchain_deepseek import ChatDeepSeek
    LANGCHAIN_AVAILABLE = True
    logger.info("✅ LangChain successfully imported")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    import traceback
    logger.error(f"❌ LangChain import failed: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    logger.warning("Install: pip install langchain langchain-deepseek")

# Create FastAPI app
app = FastAPI(
    title="Company Lookup API",
    description="API para buscar información de empresas y keywords usando Apify",
    version="1.0.0"
)


#deepseek

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
class AgentResponse(BaseModel):
    company_name: str
    short_description: str
    keywords: List[str]
    logo_url: Optional[str] = None
    domain: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class CompanyLookupResponse(BaseModel):
    status: str
    company: str
    keywords: List[str]
    agent: Optional[AgentResponse] = None
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


def get_deepseek_llm(language: str = "es"):
    """Get DeepSeek LLM instance."""
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain not available. Install langchain and langchain-deepseek packages.")
        return None
    
    api_key = os.getenv("DEEPSEEK_API")
    if not api_key:
        logger.warning("DEEPSEEK_API not set. Agent functionality disabled.")
        return None
    
    # Set DEEPSEEK_API_KEY for langchain-deepseek (it expects this env var)
    os.environ["DEEPSEEK_API_KEY"] = api_key
    
    try:
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        logger.info("DeepSeek LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Error initializing DeepSeek LLM: {e}", exc_info=True)
        return None


def get_company_info_and_keywords_agent(company_name: str, language: str = "es", country_code: Optional[str] = None, organic_titles: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Agent combinado: Obtener información de la empresa Y generar keywords en una sola llamada.
    
    Args:
        company_name: Nombre de la empresa
        language: Código de idioma (es, en, etc.)
        country_code: Código de país (PE, US, ES, etc.)
        organic_titles: Lista de títulos únicos de organicResults para usar como referencia
    
    Returns:
        Dict with company_name, short_description, keywords, additional_data (keys in English)
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    llm = get_deepseek_llm(language)
    if not llm:
        return None
    
    try:
        logger.info(f"Running combined agent for: {company_name} (country: {country_code}, language: {language}, {len(organic_titles or [])} organic titles)")
        
        country_context = ""
        if country_code:
            country_context = f"\n\nIMPORTANTE: La empresa está ubicada o opera principalmente en el país con código: {country_code}. Considera el contexto local, mercado, regulaciones y cultura de este país al proporcionar la información."
        
        organic_context = ""
        if organic_titles:
            titles_text = "\n".join([f"- {title}" for title in organic_titles[:20]])  # Limitar a 20 títulos
            organic_context = f"\n\nREFERENCIAS DE BÚSQUEDA (títulos de resultados orgánicos encontrados sobre esta empresa):\n{titles_text}\n\nUsa estos títulos como referencia para entender mejor qué hace la empresa, sus productos, servicios y actividades. Estos resultados provienen de búsquedas reales en Google."
        
        prompt_text = f"""Eres un experto en investigación de empresas y marketing digital. Analiza la empresa "{company_name}" y proporciona:

1. Nombre oficial de la empresa
2. Descripción corta (2-3 oraciones) de qué hace la empresa
3. Datos adicionales relevantes (sector, ubicación, año de fundación, mercado objetivo, productos, servicios, etc.)
4. Lista de palabras clave relevantes (5-10 keywords){country_context}{organic_context}

REGLAS ESTRICTAS PARA KEYWORDS:
- NUNCA incluyas el nombre de la empresa o marca en las keywords
- NUNCA incluyas variaciones del nombre de la empresa (ej: "rokys", "Rokys", "ROKYS", "roky's", etc.)
- Las keywords deben ser términos genéricos que los clientes buscarían, SIN mencionar la marca
- Si el nombre de la empresa aparece en los títulos de búsqueda, IGNÓRALO y extrae solo los términos genéricos
- Las keywords deben estar relacionadas con: lo que la empresa hace o vende (genérico), productos o servicios relacionados, términos de búsqueda que los clientes podrían usar, términos específicos del mercado local

Responde en formato JSON con las siguientes claves (en inglés):
- company_name: string
- short_description: string
- keywords: array de strings (5-10 keywords genéricas, SIN incluir el nombre de la empresa)
- additional_data: object con información adicional (puede incluir: sector, industry, productos, products, servicios, services, ubicación, location, etc.)

Ejemplo de keywords CORRECTAS: ["comida criolla peruana", "restaurante familiar lima", "pollo a la brasa", "ceviche"]
Ejemplo de keywords INCORRECTAS: ["rokys", "comida rokys", "restaurante rokys"]

Responde SOLO con el JSON, sin texto adicional."""
        
        response = llm.invoke(prompt_text)
        content = response.content.strip()
        
        logger.debug(f"Raw agent response: {content[:200]}...")
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        result = json.loads(content)
        logger.info(f"Combined agent completed successfully")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in combined agent: {e}. Content: {content[:200]}")
        return None
    except Exception as e:
        logger.error(f"Error in combined agent: {e}", exc_info=True)
        return None


def get_keywords_agent(company_name: str, company_info: Optional[Dict[str, Any]], language: str = "es", country_code: Optional[str] = None, organic_titles: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    Agent 2: Generar palabras clave relacionadas con la empresa.
    
    Args:
        company_name: Nombre de la empresa
        company_info: Información de la empresa del agente 1
        language: Código de idioma (es, en, etc.)
        country_code: Código de país (PE, US, ES, etc.)
        organic_titles: Lista de títulos únicos de organicResults para usar como referencia
    
    Returns:
        List of keywords
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    llm = get_deepseek_llm(language)
    if not llm:
        return None
    
    try:
        info_context = ""
        if company_info:
            company_name_info = company_info.get('company_name') or company_info.get('nombre_empresa', company_name)
            description_info = company_info.get('short_description') or company_info.get('descripcion_corta', '')
            additional_data = company_info.get('additional_data') or company_info.get('datos_adicionales', {})
            
            # Build comprehensive context from company info
            info_context = f"\n\nINFORMACIÓN DE LA EMPRESA (usa esto como referencia para generar keywords genéricas, SIN incluir el nombre de la empresa):\n"
            info_context += f"- Descripción: {description_info}\n"
            
            if additional_data:
                if isinstance(additional_data, dict):
                    sector = additional_data.get('sector') or additional_data.get('industry', '')
                    productos = additional_data.get('productos') or additional_data.get('products', '')
                    servicios = additional_data.get('servicios') or additional_data.get('services', '')
                    
                    if sector:
                        info_context += f"- Sector/Industria: {sector}\n"
                    if productos:
                        info_context += f"- Productos: {productos}\n"
                    if servicios:
                        info_context += f"- Servicios: {servicios}\n"
            
            info_context += f"\nIMPORTANTE: Genera keywords genéricas basadas en esta información, pero NUNCA incluyas el nombre de la empresa '{company_name_info}' en ninguna keyword."
        
        country_context = ""
        if country_code:
            country_context = f"\n\nIMPORTANTE: Considera términos de búsqueda relevantes para el mercado del país {country_code}. Incluye palabras clave que sean comunes o específicas de este mercado local."
        
        organic_context = ""
        if organic_titles:
            titles_text = "\n".join([f"- {title}" for title in organic_titles[:20]])  # Limitar a 20 títulos
            organic_context = f"\n\nREFERENCIAS DE BÚSQUEDA (títulos de resultados orgánicos encontrados sobre esta empresa):\n{titles_text}\n\nUsa estos títulos para identificar palabras clave relevantes que las personas realmente buscan relacionadas con esta empresa. Extrae términos importantes de estos títulos y genera keywords basadas en ellos."
        
        prompt_text = f"""Eres un experto en marketing digital y SEO. Para la empresa "{company_name}"{info_context}{country_context}{organic_context}, genera una lista de palabras clave relevantes.

REGLAS ESTRICTAS - DEBES CUMPLIR:
1. NUNCA incluyas el nombre de la empresa o marca en las palabras clave
2. NUNCA incluyas variaciones del nombre de la empresa (ej: "rokys", "Rokys", "ROKYS", "roky's", "Roky's", etc.)
3. Las palabras clave deben ser términos genéricos que los clientes buscarían, SIN mencionar la marca
4. Si el nombre de la empresa aparece en los títulos de búsqueda, IGNÓRALO y extrae solo los términos genéricos

Las palabras clave deben estar relacionadas con:
- Lo que la empresa hace o vende (genérico, sin marca)
- Productos o servicios relacionados (términos genéricos)
- Términos de búsqueda que los clientes podrían usar (sin mencionar la marca)
- Términos específicos del mercado local (si aplica)
- Términos extraídos de los títulos de búsqueda proporcionados (pero sin incluir el nombre de la empresa)

Genera entre 5 y 10 palabras clave. Responde SOLO con un array JSON de strings, sin texto adicional.

Ejemplo CORRECTO: ["comida criolla peruana", "restaurante familiar lima", "pollo a la brasa", "ceviche", "anticuchos", "lomo saltado", "restaurante tradicional peruano"]
Ejemplo INCORRECTO: ["rokys", "comida rokys", "restaurante rokys", "rokys lima", "rokys carta"]"""
        
        response = llm.invoke(prompt_text)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        keywords = json.loads(content)
        if isinstance(keywords, list):
            return keywords
        return []
    except Exception as e:
        logger.error(f"Error in keywords agent: {e}")
        return None


def extract_organic_titles(results: Dict[str, Any]) -> List[str]:
    """
    Extract unique titles from organicResults in the search results.
    
    Args:
        results: Results dictionary from lookup_company
        
    Returns:
        List of unique titles from organicResults
    """
    titles = []
    
    if not isinstance(results, dict):
        return titles
    
    # Check if results has organicResults directly
    organic_results = results.get("organicResults", [])
    
    # Check in company_results (list of items from Apify)
    if not organic_results:
        company_results = results.get("company_results", [])
        if isinstance(company_results, list):
            for item in company_results:
                if isinstance(item, dict):
                    # Check if item itself has organicResults
                    if "organicResults" in item:
                        item_organic = item.get("organicResults", [])
                        if item_organic:
                            for org_item in item_organic:
                                if isinstance(org_item, dict) and "title" in org_item:
                                    title = org_item.get("title", "").strip()
                                    if title and title not in titles:
                                        titles.append(title)
                    # Or if item is an organic result itself (direct structure)
                    elif "title" in item:
                        title = item.get("title", "").strip()
                        if title and title not in titles:
                            titles.append(title)
    
    # Extract titles from organicResults if found at top level
    if organic_results:
        for item in organic_results:
            if isinstance(item, dict) and "title" in item:
                title = item.get("title", "").strip()
                if title and title not in titles:
                    titles.append(title)
    
    # Also check keyword_results
    keyword_results = results.get("keyword_results", {})
    if isinstance(keyword_results, dict):
        for keyword, keyword_data in keyword_results.items():
            if isinstance(keyword_data, list):
                for item in keyword_data:
                    if isinstance(item, dict):
                        if "organicResults" in item:
                            item_organic = item.get("organicResults", [])
                            for org_item in item_organic:
                                if isinstance(org_item, dict) and "title" in org_item:
                                    title = org_item.get("title", "").strip()
                                    if title and title not in titles:
                                        titles.append(title)
                        elif "title" in item:
                            title = item.get("title", "").strip()
                            if title and title not in titles:
                                titles.append(title)
    
    logger.info(f"Extracted {len(titles)} unique titles from organicResults")
    return titles


def extract_organic_urls(results: Dict[str, Any]) -> List[str]:
    """
    Extract unique URLs from organicResults in the search results.
    
    Args:
        results: Results dictionary from lookup_company
        
    Returns:
        List of unique URLs from organicResults
    """
    urls = []
    
    if not isinstance(results, dict):
        logger.warning("Results is not a dict, cannot extract URLs")
        return urls
    
    # Check if results has organicResults directly
    organic_results = results.get("organicResults", [])
    
    # Check in company_results (list of items from Apify)
    if not organic_results:
        company_results = results.get("company_results", [])
        if isinstance(company_results, list):
            for item in company_results:
                if isinstance(item, dict):
                    # Check if item itself has organicResults
                    if "organicResults" in item:
                        item_organic = item.get("organicResults", [])
                        if item_organic:
                            for org_item in item_organic:
                                if isinstance(org_item, dict):
                                    url = org_item.get("url") or org_item.get("displayedUrl", "")
                                    if url and url not in urls:
                                        urls.append(url)
                    # Or if item is an organic result itself (direct structure from Apify)
                    elif "url" in item or "displayedUrl" in item:
                        url = item.get("url") or item.get("displayedUrl", "")
                        if url and url not in urls:
                            urls.append(url)
    
    # Extract URLs from organicResults if found at top level
    if organic_results:
        for item in organic_results:
            if isinstance(item, dict):
                url = item.get("url") or item.get("displayedUrl", "")
                if url and url not in urls:
                    urls.append(url)
    
    # Also check keyword_results
    keyword_results = results.get("keyword_results", {})
    if isinstance(keyword_results, dict):
        for keyword, keyword_data in keyword_results.items():
            if isinstance(keyword_data, list):
                for item in keyword_data:
                    if isinstance(item, dict):
                        if "organicResults" in item:
                            item_organic = item.get("organicResults", [])
                            for org_item in item_organic:
                                if isinstance(org_item, dict):
                                    url = org_item.get("url") or org_item.get("displayedUrl", "")
                                    if url and url not in urls:
                                        urls.append(url)
                        elif "url" in item or "displayedUrl" in item:
                            url = item.get("url") or item.get("displayedUrl", "")
                            if url and url not in urls:
                                urls.append(url)
    
    logger.info(f"Extracted {len(urls)} unique URLs from organicResults")
    if urls:
        logger.info(f"Sample URLs: {urls[:3]}")
    else:
        logger.warning(f"No URLs extracted! Results keys: {list(results.keys())[:10]}")
        # Debug: check structure
        if "company_results" in results:
            company_results = results.get("company_results", [])
            if company_results and isinstance(company_results, list) and len(company_results) > 0:
                first_item = company_results[0]
                if isinstance(first_item, dict):
                    logger.info(f"First company_result keys: {list(first_item.keys())[:10]}")
    
    return urls


def get_domain_agent(company_name: str, urls: List[str], language: str = "es") -> Optional[str]:
    """
    Agent 3: Determinar el dominio principal de la empresa a partir de las URLs.
    
    Args:
        company_name: Nombre de la empresa
        urls: Lista de URLs de organicResults
        language: Código de idioma (es, en, etc.)
    
    Returns:
        Dominio principal (ej: "rokys.com") o None
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    if not urls:
        return None
    
    llm = get_deepseek_llm(language)
    if not llm:
        return None
    
    try:
        logger.info(f"Running domain agent for: {company_name} with {len(urls)} URLs")
        
        # Extract domains from URLs
        domains = []
        for url in urls[:20]:  # Limit to 20 URLs
            try:
                parsed = urlparse(url)
                domain = parsed.netloc or parsed.path.split('/')[0]
                if domain and domain not in domains:
                    domains.append(domain)
            except Exception:
                continue
        
        if not domains:
            return None
        
        domains_text = "\n".join([f"- {domain}" for domain in domains])
        
        prompt_text = f"""Eres un experto en identificar dominios web oficiales de empresas. Para la empresa "{company_name}", analiza las siguientes URLs/dominios encontrados en resultados de búsqueda:

{domains_text}

Determina cuál es el dominio PRINCIPAL y OFICIAL de la empresa. Este debe ser:
- El dominio principal del sitio web oficial
- No subdominios (ej: blog.ejemplo.com)
- No dominios de terceros (ej: facebook.com, instagram.com, linkedin.com)
- El dominio más relevante y oficial

Responde SOLO con el dominio (ej: "rokys.com"), sin "https://", sin "http://", sin "www.", sin texto adicional."""
        
        response = llm.invoke(prompt_text)
        content = response.content.strip()
        
        # Clean up the response
        content = content.replace("https://", "").replace("http://", "").replace("www.", "")
        content = content.split("/")[0].split("?")[0].strip()
        
        logger.info(f"Domain agent determined: {content}")
        return content if content else None
    except Exception as e:
        logger.error(f"Error in domain agent: {e}", exc_info=True)
        return None


def get_logo_url(domain: str) -> Optional[str]:
    """
    Get logo URL using Clearbit Logo API.
    
    Args:
        domain: Company domain (e.g., "rokys.com")
        
    Returns:
        Logo URL or None
    """
    if not domain:
        return None
    
    # Clean domain
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").strip()
    
    # Clearbit Logo API
    logo_url = f"https://logo.clearbit.com/{domain}"
    
    logger.info(f"Generated Clearbit logo URL: {logo_url}")
    return logo_url


# Persistent cache configuration
_agent_cache_dir = Path("/tmp/agent_cache")  # Cache for agent responses
_apify_cache_dir = Path("/tmp/apify_cache")  # Cache for Apify results
_cache_max_size = 10  # Increased cache size
#cada 5 minutos
_cache_ttl_hours = 5/60

# Initialize cache directories at module load
for cache_dir in [_agent_cache_dir, _apify_cache_dir]:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Cache directory initialized: {cache_dir}")
        logger.info(f"   Cache directory exists: {cache_dir.exists()}")
        logger.info(f"   Cache directory writable: {os.access(cache_dir, os.W_OK)}")
    except Exception as e:
        logger.error(f"❌ Failed to create cache directory {cache_dir}: {e}", exc_info=True)

def _get_cache_stats(cache_type: str = "agent") -> Dict[str, Any]:
    """Get cache statistics for debugging."""
    try:
        cache_dir = _agent_cache_dir if cache_type == "agent" else _apify_cache_dir
        cache_files = list(cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        return {
            "cache_dir": str(cache_dir),
            "cache_dir_exists": cache_dir.exists(),
            "cache_dir_writable": os.access(cache_dir, os.W_OK),
            "total_files": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}


def _get_apify_cache_key(company: str, keywords: Optional[List[str]], country_code: Optional[str], language_code: Optional[str], max_items_per_query: int) -> str:
    """
    Generate a cache key for Apify results.
    """
    keywords_str = "|".join(sorted(keywords or []))
    key_parts = [
        company.lower().strip(),
        language_code or "es",
        country_code or "",
        str(max_items_per_query),
        hashlib.md5(keywords_str.encode()).hexdigest()[:8] if keywords_str else ""
    ]
    key_string = "|".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _load_apify_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Load Apify results from cache.
    """
    cache_file = _get_cache_file_path(cache_key, "apify")
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache entry is expired
        cached_time_str = cache_data.get('timestamp', '')
        if not cached_time_str:
            cache_file.unlink()
            return None
        
        cached_time = datetime.fromisoformat(cached_time_str)
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=_cache_ttl_hours):
            logger.info(f"Apify cache entry expired (age: {age.total_seconds()/3600:.1f}h)")
            cache_file.unlink()
            return None
        
        results = cache_data.get('results', {})
        logger.info(f"✅✅✅ APIFY CACHE HIT - Using cached results (NO APIFY API CALLS - SAVING CREDITS)")
        logger.info(f"   Cache age: {age.total_seconds()/60:.1f} minutes")
        return results
    except Exception as e:
        logger.warning(f"Error loading Apify cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_apify_cache(cache_key: str, results: Dict[str, Any]) -> None:
    """
    Save Apify results to cache.
    """
    try:
        cache_file = _get_cache_file_path(cache_key, "apify")
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # Write atomically
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved Apify cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        # Clean up old cache files
        _cleanup_old_cache("apify")
    except Exception as e:
        logger.error(f"Error saving Apify cache: {e}", exc_info=True)

def _get_cache_key(company_name: str, language_code: Optional[str], country_code: Optional[str]) -> str:
    """
    Generate a cache key from user input parameters only.
    Does NOT include organic_titles to ensure same company = same cache key.
    """
    language = language_code or "es"
    
    key_parts = [
        company_name.lower().strip(),
        language,
        country_code or ""
    ]
    key_string = "|".join(key_parts)
    # Create a safe filename from the key
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def _get_cache_file_path(cache_key: str, cache_type: str = "agent") -> Path:
    """Get the cache file path for a given key."""
    cache_dir = _agent_cache_dir if cache_type == "agent" else _apify_cache_dir
    return cache_dir / f"{cache_key}.json"


def _load_cache_entry(cache_key: str) -> Optional[AgentResponse]:
    """
    Load a cache entry from disk (for agent responses).
    Returns None if not found or expired.
    """
    cache_file = _get_cache_file_path(cache_key, "agent")
    
    if not cache_file.exists():
        logger.debug(f"Cache file not found: {cache_file.name}")
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache entry is expired
        cached_time_str = cache_data.get('timestamp', '')
        if not cached_time_str:
            logger.warning(f"Cache entry has no timestamp: {cache_file.name}")
            cache_file.unlink()
            return None
        
        cached_time = datetime.fromisoformat(cached_time_str)
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=_cache_ttl_hours):
            logger.info(f"Cache entry expired (age: {age.total_seconds()/3600:.1f}h) for key: {cache_key[:16]}...")
            cache_file.unlink()  # Delete expired cache file
            return None
        
        # Convert dict back to AgentResponse
        response_data = cache_data.get('response', {})
        if not response_data:
            logger.warning(f"Cache entry has no response data: {cache_file.name}")
            cache_file.unlink()
            return None
        
        agent_response = AgentResponse(**response_data)
        logger.info(f"✅ Cache loaded successfully (age: {age.total_seconds()/60:.1f}min)")
        return agent_response
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error loading cache entry {cache_key[:16]}...: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None
    except Exception as e:
        logger.warning(f"Error loading cache entry {cache_key[:16]}...: {e}", exc_info=True)
        # Delete corrupted cache file
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_cache_entry(cache_key: str, response: AgentResponse) -> None:
    """
    Save a cache entry to disk (for agent responses).
    """
    try:
        cache_file = _get_cache_file_path(cache_key, "agent")
        
        # Convert response to dict
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        elif hasattr(response, 'dict'):
            response_dict = response.dict()
        else:
            response_dict = dict(response)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'response': response_dict
        }
        
        # Write atomically (write to temp file then rename)
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # Atomic rename
        temp_file.replace(cache_file)
        
        logger.info(f"✅ Saved cache entry: {cache_key[:16]}... (file: {cache_file.name})")
        
        # Clean up old cache files if cache is too large
        _cleanup_old_cache("agent")
    except Exception as e:
        logger.error(f"Error saving cache entry: {e}", exc_info=True)


def _cleanup_old_cache(cache_type: str = "agent") -> None:
    """
    Remove old cache files if cache directory is too large.
    Keeps the most recent _cache_max_size entries.
    """
    try:
        cache_dir = _agent_cache_dir if cache_type == "agent" else _apify_cache_dir
        cache_files = list(cache_dir.glob("*.json"))
        
        if len(cache_files) <= _cache_max_size:
            return
        
        # Sort by modification time (oldest first)
        cache_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Remove oldest files
        files_to_remove = cache_files[:-_cache_max_size]
        for cache_file in files_to_remove:
            try:
                cache_file.unlink()
                logger.info(f"Removed old cache file: {cache_file.name}")
            except Exception as e:
                logger.warning(f"Error removing cache file {cache_file.name}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning up cache: {e}")


def get_agent_response(company_name: str, language_code: Optional[str] = None, country_code: Optional[str] = None, organic_titles: Optional[List[str]] = None, organic_urls: Optional[List[str]] = None) -> Optional[AgentResponse]:
    """
    Get agent response using 3 agents with DeepSeek API.
    Uses LRU cache to optimize repeated calls.
    
    Args:
        company_name: Company name to analyze
        language_code: Language code (default: "es")
        country_code: Country code (PE, US, ES, etc.)
        organic_titles: List of unique titles from organicResults to use as reference
        organic_urls: List of unique URLs from organicResults to determine domain
        
    Returns:
        AgentResponse with company info, keywords, domain and logo
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    # Check cache first (persistent cache) - based on user input only
    cache_key = _get_cache_key(company_name, language_code, country_code)
    cache_file = _get_cache_file_path(cache_key)
    
    # Log cache stats for debugging
    cache_stats = _get_cache_stats("agent")
    logger.info(f"🔍 Checking AGENT cache for: {company_name} (language: {language_code or 'es'}, country: {country_code or 'none'})")
    logger.info(f"   Cache key: {cache_key[:16]}...")
    logger.info(f"   Cache file: {cache_file.name} (exists: {cache_file.exists()})")
    logger.info(f"   Cache stats: {cache_stats.get('total_files', 0)} files, {cache_stats.get('total_size_mb', 0)} MB, writable: {cache_stats.get('cache_dir_writable', False)}")
    
    cached_response = _load_cache_entry(cache_key)
    
    if cached_response:
        logger.info(f"✅✅✅ CACHE HIT - Returning cached response (NO API CALLS WILL BE MADE - SAVING CREDITS)")
        logger.info(f"   Company: {cached_response.company_name}")
        logger.info(f"   Keywords count: {len(cached_response.keywords)}")
        logger.info(f"   Domain: {cached_response.domain}")
        logger.info(f"   Logo URL: {cached_response.logo_url}")
        return cached_response
    
    logger.warning(f"❌❌❌ CACHE MISS - Will make API calls to DeepSeek (this will consume credits)")
    logger.warning(f"   Cache file does not exist or is expired: {cache_file.name}")
    if not cache_stats.get('cache_dir_writable', False):
        logger.error(f"⚠️⚠️⚠️ WARNING: Cache directory is NOT writable! Cache will not persist!")
    
    language = language_code or "es"
    organic_titles = organic_titles or []
    organic_urls = organic_urls or []
    
    try:
        logger.info(f"Running agents for company: {company_name} (country: {country_code}, language: {language}, {len(organic_titles)} organic titles, {len(organic_urls)} URLs)")
        
        # Agent 1: Combined company info and keywords (saves one API call)
        company_data = get_company_info_and_keywords_agent(company_name, language, country_code, organic_titles)
        
        if not company_data:
            return None
        
        # Extract data from combined agent response
        company_info = {
            "company_name": company_data.get("company_name", company_data.get("nombre_empresa", company_name)),
            "short_description": company_data.get("short_description", company_data.get("descripcion_corta", "")),
            "additional_data": company_data.get("additional_data", company_data.get("datos_adicionales"))
        }
        keywords = company_data.get("keywords", [])
        
        # Agent 2: Domain determination
        domain = None
        logo_url = None
        
        if organic_urls:
            logger.info(f"Running domain agent with {len(organic_urls)} URLs")
            domain = get_domain_agent(company_name, organic_urls, language)
            if domain:
                logger.info(f"✅ Domain determined: {domain}")
                # Get logo URL using Clearbit
                logo_url = get_logo_url(domain)
                logger.info(f"✅ Logo URL generated: {logo_url}")
            else:
                logger.warning("⚠️ Domain agent returned None")
        else:
            logger.warning("⚠️ No organic URLs available for domain agent")
        
        if not company_info:
            return None
        
        response = AgentResponse(
            company_name=company_info.get("company_name", company_name),
            short_description=company_info.get("short_description", ""),
            keywords=keywords or [],
            domain=domain,
            logo_url=logo_url,
            additional_data=company_info.get("additional_data")
        )
        
        # Store in persistent cache
        _save_cache_entry(cache_key, response)
        logger.info(f"✅ Cached response for company: {company_name} (key: {cache_key[:16]}...)")
        
        return response
    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
        return None


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
    
    # Check Apify cache first
    if use_cache and not force_refresh:
        apify_cache_key = _get_apify_cache_key(company, keywords, country_code, language_code, max_items_per_query)
        cached_results = _load_apify_cache(apify_cache_key)
        
        if cached_results:
            logger.info(f"✅✅✅ Using cached Apify results - NO APIFY API CALLS")
            return cached_results
        
        logger.warning(f"❌❌❌ Apify cache MISS - Will make Apify API calls (this will consume Apify credits)")
        logger.info(f"   Apify cache key: {apify_cache_key[:16]}...")
    elif force_refresh:
        logger.info(f"🔄 Force refresh requested - ignoring Apify cache")
    
    try:
        logger.info(f"Starting company lookup for: {company} (making Apify API calls...)")
        
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
        
        # Save to Apify cache after getting company results
        if use_cache:
            apify_cache_key = _get_apify_cache_key(company, keywords, country_code, language_code, max_items_per_query)
            _save_apify_cache(apify_cache_key, results)
            logger.info(f"✅ Cached Apify results for future requests")
        
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
        
        # Update Apify cache with keyword results
        if use_cache:
            apify_cache_key = _get_apify_cache_key(company, keywords, country_code, language_code, max_items_per_query)
            _save_apify_cache(apify_cache_key, results)
            logger.info(f"✅ Updated Apify cache with keyword results")
        
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
        
        # Extract organic titles and URLs from results to use as reference in agent prompts
        organic_titles = extract_organic_titles(results)
        organic_urls = extract_organic_urls(results)
        
        # Get agent response with DeepSeek
        logger.info(f"Getting agent response for company: {request.company}")
        logger.info(f"LANGCHAIN_AVAILABLE: {LANGCHAIN_AVAILABLE}")
        logger.info(f"Found {len(organic_titles)} unique organic titles and {len(organic_urls)} URLs to use as reference")
        deepseek_key = os.getenv('DEEPSEEK_API')
        logger.info(f"DEEPSEEK_API set: {bool(deepseek_key)}")
        if deepseek_key:
            logger.info(f"DEEPSEEK_API length: {len(deepseek_key)} (first 10 chars: {deepseek_key[:10]}...)")
        else:
            logger.warning("⚠️ DEEPSEEK_API is not set! Configure it in GitHub Secrets or Cloud Run environment variables.")
        
        agent_response = None
        if not LANGCHAIN_AVAILABLE:
            logger.error("❌ LangChain is not available. Check Dockerfile build logs for installation errors.")
        elif not deepseek_key:
            logger.error("❌ DEEPSEEK_API is not configured. Add it to GitHub Secrets: DEEPSEEK_API")
        else:
            try:
                agent_response = get_agent_response(
                    request.company, 
                    request.language_code, 
                    request.country_code,
                    organic_titles,
                    organic_urls
                )
                if agent_response:
                    logger.info(f"✅ Agent response generated successfully: {agent_response.company_name}")
                else:
                    logger.warning("⚠️ Agent response is None - check get_agent_response function logs")
            except Exception as e:
                logger.error(f"❌ Error getting agent response: {e}", exc_info=True)
        
        logger.info(f"Lookup completed: company={request.company}, total_results={summary.get('total_company_results', 0) + summary.get('total_keyword_results', 0)}")
        
        return CompanyLookupResponse(
            status="success",
            company=results.get("company", request.company),
            keywords=results.get("keywords", request.keywords or []),
            agent=agent_response,
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

