"""
Analytics Opportunity Module
Author: Mauricio J. @synaw_w
"""

import logging
import os
import json
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
from src.modules.supabase_connection import get_supabase_client

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from langchain_deepseek import ChatDeepSeek
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_deepseek_llm = None


def _get_deepseek_llm():
    """Get or create DeepSeek LLM instance (singleton)."""
    global _deepseek_llm
    if _deepseek_llm is None:
        if not LANGCHAIN_AVAILABLE:
            logger.warning("⚠️  LangChain not available")
            return None
        
        api_key = os.getenv("DEEPSEEK_API")
        if not api_key:
            logger.warning("⚠️  DEEPSEEK_API not set")
            return None
        
        try:
            _deepseek_llm = ChatDeepSeek(
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=api_key
            )
            logger.info("✅ DeepSeek LLM initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize DeepSeek LLM: {e}")
            return None
    
    return _deepseek_llm


def get_business_opportunity(query: str, id_company: int = 1, limit: int = 100) -> Dict[str, Any]:
    """
    Obtener los últimos 100 posts y usar agente DeepSeek iterativo para generar oportunidades de negocio.
    
    Args:
        query: Query para filtrar posts
        id_company: Company ID (default: 1)
        limit: Número máximo de posts a analizar (default: 100)
        
    Returns:
        Dict with results (array of opportunities) and error (optional)
    """
    try:
        logger.info(f"🔍 Generating business opportunity from posts for query: '{query}' (company: {id_company})")
        
        if not query or not query.strip():
            logger.warning("⚠️  Empty query provided")
            return {
                "query": query,
                "results": [],
                "error": "Empty query provided"
            }
        
        query_clean = query.strip()
        supabase = get_supabase_client()
        
        keyword_pattern = f"%{query_clean.lower()}%"
        
        query_title = supabase.table("posts").select("id,title,description,source").eq("id_company", id_company).ilike("title", keyword_pattern)
        query_desc = supabase.table("posts").select("id,title,description,source").eq("id_company", id_company).ilike("description", keyword_pattern)
        
        response_title = query_title.execute()
        response_desc = query_desc.execute()
        
        posts_title = {post["id"]: post for post in (response_title.data or [])}
        posts_desc = {post["id"]: post for post in (response_desc.data or [])}
        
        all_posts_dict = {**posts_title, **posts_desc}
        posts_list = list(all_posts_dict.values())[:limit]
        
        if len(posts_list) == 0:
            logger.warning(f"⚠️  No posts found for query: '{query_clean}'")
            return {
                "query": query_clean,
                "results": [],
                "error": "No posts found"
            }
        
        logger.info(f"📊 Analyzing {len(posts_list)} posts for business opportunity extraction")
        
        posts_array = []
        post_id_mapping = {}
        for idx, post in enumerate(posts_list):
            post_id = post.get("id")
            title = post.get("title", "")
            description = post.get("description", "")
            source = post.get("source", "")
            
            post_data = {
                "index": idx,
                "id": post_id,
                "title": title.strip() if title else "",
                "description": description.strip() if description else "",
                "source": source
            }
            posts_array.append(post_data)
            post_id_mapping[idx] = post_id
        
        if len(posts_array) == 0:
            logger.warning("⚠️  No valid posts found")
            return {
                "query": query_clean,
                "results": [],
                "error": "No valid posts found"
            }
        
        llm = _get_deepseek_llm()
        if not llm:
            logger.error("❌ DeepSeek LLM not available")
            return {
                "query": query_clean,
                "results": [],
                "error": "DeepSeek LLM not available"
            }
        
        posts_json = json.dumps(posts_array, ensure_ascii=False, indent=2)
        
        logger.info(f"🤖 Starting iterative DeepSeek agent (2 steps) to generate business opportunities...")
        
        step1_prompt = f"""Eres un analista experto en descubrir fenómenos emergentes específicos en datos de redes sociales. Tu trabajo es identificar menciones concretas, opiniones específicas, sugerencias reales y quejas a competencia.

ARRAY DE POSTS (mantén este formato JSON):
{posts_json}

PASO 1 - IDENTIFICACIÓN DE FENÓMENOS EMERGENTES ESPECÍFICOS:
Analiza el array de posts buscando menciones CONCRETAS y ESPECÍFICAS. NO hagas generalizaciones. Identifica:

1. TEMAS EMERGENTES ESPECÍFICOS: ¿De qué se habla específicamente? (ej: "se habla de X", "mencionan Y")
2. OPINIONES CONCRETAS: ¿Qué opiniones específicas expresan los usuarios? (ej: "algunas personas dicen que...", "hay opiniones de que...")
3. SUGERENCIAS REALES: ¿Qué sugerencias específicas hacen los usuarios? (ej: "alguien sugirió...", "proponen...")
4. QUEJAS A COMPETENCIA: ¿Qué quejas específicas hay sobre competidores? (ej: "la queja a tu competencia es...", "mencionan que X hace mal...")
5. NECESIDADES MENCIONADAS: ¿Qué necesidades específicas mencionan? (ej: "piden...", "solicitan...", "necesitan...")
6. PATRONES DE COMPORTAMIENTO: ¿Qué comportamientos específicos observas? (ej: "cuando X, entonces Y", "siempre que...")
7. CONTRADICCIONES ESPECÍFICAS: ¿Qué contradicciones concretas encuentras? (ej: "dicen X pero hacen Y", "quieren A pero no B")

IMPORTANTE: 
- Sé ESPECÍFICO, no genérico
- Cita o parafrasea lo que realmente dicen los posts
- Identifica menciones concretas, no interpretaciones vagas
- Busca patrones en lo que realmente se menciona, no en lo que asumes

Responde SOLO con un JSON que contenga:
- "emerging_topics": un array con temas específicos de los que se habla (ej: "se habla de X", "mencionan Y"). Mínimo 3, máximo 7.
- "specific_opinions": un array con opiniones concretas expresadas (ej: "algunas personas dicen que X", "hay opiniones de que Y"). Mínimo 3.
- "user_suggestions": un array con sugerencias específicas que hacen los usuarios (ej: "alguien sugirió X", "proponen Y"). Mínimo 2.
- "competitor_complaints": un array con quejas específicas sobre competencia (ej: "la queja a tu competencia es X", "mencionan que Y hace mal Z"). Incluye todas las que encuentres.
- "mentioned_needs": un array con necesidades específicas mencionadas (ej: "piden X", "solicitan Y", "necesitan Z"). Mínimo 3.
- "behavior_patterns": un array con patrones de comportamiento específicos observados (ej: "cuando X, entonces Y", "siempre que A, hacen B"). Mínimo 2.
- "specific_contradictions": un array con contradicciones concretas (ej: "dicen X pero hacen Y", "quieren A pero no B"). Incluye todas las que encuentres.

Responde SOLO con el JSON, sin texto adicional."""
        
        logger.info("🤖 Step 1: Initial analysis...")
        step1_response = llm.invoke(step1_prompt)
        step1_content = step1_response.content.strip()
        
        if step1_content.startswith("```json"):
            step1_content = step1_content.replace("```json", "").replace("```", "").strip()
        elif step1_content.startswith("```"):
            step1_content = step1_content.replace("```", "").strip()
        
        try:
            step1_result = json.loads(step1_content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Step 1 JSON decode error: {e}")
            return {
                "query": query_clean,
                "results": [],
                "error": f"Error in step 1: {str(e)}"
            }
        
        step2_prompt = f"""Eres un estratega de negocio experto en descubrir oportunidades basadas en fenómenos emergentes específicos. Tu misión es identificar insights concretos que generen valor real.

ARRAY DE POSTS (mantén este formato JSON):
{posts_json}

FENÓMENOS EMERGENTES IDENTIFICADOS EN EL PASO 1:
{json.dumps(step1_result, ensure_ascii=False, indent=2)}

PASO 2 - GENERACIÓN DE OPORTUNIDADES BASADAS EN FENÓMENOS EMERGENTES ESPECÍFICOS:
Basándote en los fenómenos emergentes específicos del Paso 1, genera entre 1 y 5 oportunidades de negocio. Cada oportunidad DEBE estar fundamentada en menciones concretas, opiniones específicas, sugerencias reales o quejas identificadas.

REGLAS CRÍTICAS:
1. Los insights DEBEN ser ESPECÍFICOS y mencionar fenómenos concretos encontrados
2. Usa lenguaje como: "se habla de...", "hay opiniones de que...", "alguien sugirió...", "la queja a tu competencia es...", "algunas personas dicen que..."
3. NO hagas generalizaciones vagas. Cita o parafrasea lo que realmente se menciona en los posts
4. Cada insight debe mencionar fenómenos emergentes específicos, no observaciones genéricas
5. Conecta los fenómenos emergentes con oportunidades de negocio concretas
6. Prioriza oportunidades basadas en quejas a competencia, sugerencias específicas o necesidades mencionadas

ESTRUCTURA REQUERIDA para cada oportunidad:
- "insight": un texto MUY CORTO (1-2 oraciones máximo) que describe el EVENTO ESPECÍFICO que es una ventana de oportunidad. Debe:
  * Ser directo y conciso - solo el evento/fenómeno que genera valor
  * Mencionar específicamente qué se dice, qué se queja, qué se sugiere
  * Usar lenguaje concreto: "Hay gente comentando que...", "Se quejan de que...", "Alguien mencionó que...", "La queja a tu competencia es..."
  * NO incluir explicaciones largas ni análisis - solo el evento específico
  * Basarse en menciones reales de los posts
  
  EJEMPLOS DE INSIGHTS VÁLIDOS (CORTOS Y DIRECTOS):
   "Hay gente comentando que las prendas de shein son de mala calidad"
   "Se quejan de que los tiempos de espera son muy largos en horarios pico"
   "Alguien mencionó que falta variedad en opciones vegetarianas"
   "La queja a tu competencia es que no tienen opciones sin gluten"
   "Hay opiniones de que los precios de delivery son más altos que en el local"
   "Algunas personas dicen que nunca llegan a tiempo a las promociones por stock limitado"
  
  EJEMPLOS DE INSIGHTS INVÁLIDOS (MUY LARGOS O GENÉRICOS):
   "Hay opiniones de que 'nunca había llegado primera a una promo' y mencionan que 'este pollo vuela', mostrando que las promociones generan alta demanda pero también frustración por stock limitado. Alguien sugirió que Rokyto debería visitar más distritos además de Comas, indicando interés en mayor accesibilidad geográfica."
   "Los usuarios disfrutan de colaboraciones con otras marcas"
   "Las personas buscan productos de calidad"
   "Los eventos temáticos generan engagement"

- "ideas": un array con 1 a 3 ideas cortas y concretas de cómo aprovechar este fenómeno emergente para generar valor. Cada idea debe ser específica y accionable (1-2 oraciones)
- "posts": un array de números enteros que representan los índices del array original de posts que respaldan este insight (mínimo 2 índices, máximo 8 índices). Solo incluye índices válidos (0 a {len(posts_array)-1})

Responde SOLO con un JSON que contenga:
- "opportunities": un array con 1 a 5 objetos, cada uno con la estructura: {{"insight": "...", "ideas": ["...", "..."], "posts": [índices]}}

Responde SOLO con el JSON, sin texto adicional."""
        
        logger.info("🤖 Step 2: Business opportunities generation...")
        step2_response = llm.invoke(step2_prompt)
        step2_content = step2_response.content.strip()
        
        if step2_content.startswith("```json"):
            step2_content = step2_content.replace("```json", "").replace("```", "").strip()
        elif step2_content.startswith("```"):
            step2_content = step2_content.replace("```", "").strip()
        
        try:
            step2_result = json.loads(step2_content)
            
            if isinstance(step2_result, list):
                opportunities = step2_result
            elif isinstance(step2_result, dict):
                opportunities = step2_result.get("opportunities", [])
            else:
                opportunities = []
            
            if not isinstance(opportunities, list):
                opportunities = []
            
            results = []
            all_post_ids = set()
            opportunity_post_ids = []
            
            for opp in opportunities:
                if not isinstance(opp, dict):
                    continue
                
                insight = opp.get("insight", "")
                ideas = opp.get("ideas", [])
                posts_indices = opp.get("posts", [])
                
                if not isinstance(ideas, list):
                    ideas = []
                if not isinstance(posts_indices, list):
                    posts_indices = []
                
                valid_indices = [idx for idx in posts_indices if isinstance(idx, int) and 0 <= idx < len(posts_array)]
                post_ids = [post_id_mapping[idx] for idx in valid_indices if idx in post_id_mapping]
                all_post_ids.update(post_ids)
                
                if insight or ideas:
                    results.append({
                        "insight": insight,
                        "ideas": ideas[:3],
                        "posts": post_ids
                    })
                    opportunity_post_ids.append(post_ids)
            
            if len(all_post_ids) > 0:
                logger.info(f"📥 Fetching {len(all_post_ids)} posts from database...")
                posts_query = supabase.table("posts").select("*").in_("id", list(all_post_ids)).eq("id_company", id_company)
                posts_response = posts_query.execute()
                posts_data = {post["id"]: post for post in (posts_response.data or [])}
                
                for i, result in enumerate(results):
                    post_ids = result.get("posts", [])
                    full_posts = [posts_data[post_id] for post_id in post_ids if post_id in posts_data]
                    results[i]["posts"] = full_posts
            
            logger.info(f"✅ Generated {len(results)} business opportunities with {len(all_post_ids)} unique post IDs")
            
            return {
                "query": query_clean,
                "results": results,
                "error": None
            }
        except json.JSONDecodeError as e:
            logger.error(f"❌ Step 2 JSON decode error: {e}. Content: {step2_content[:200]}")
            return {
                "query": query_clean,
                "results": [],
                "error": f"Error in step 2: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"❌ Error generating business opportunity: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "query": query,
            "results": [],
            "error": str(e)
        }

