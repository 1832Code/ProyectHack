"""
Analytics Module
Author: Mauricio J. @synaw_w
"""

import logging
import re
import os
import json
import hashlib
from typing import Optional, Dict, Any, List
from collections import Counter
from pathlib import Path
from datetime import datetime, timedelta
from src.modules.supabase_connection import get_supabase_client
from src.modules.word_lists import POSITIVE_WORDS, NEGATIVE_WORDS, SPANISH_STOPWORDS

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
    logger.warning("langchain-deepseek not available")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_sentiment_analyzer = None
_nlp = None
_deepseek_llm = None

_keywords_cache_dir = Path("/tmp/keywords_cache")
_keywords_cache_ttl_minutes = 10

try:
    _keywords_cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Keywords cache directory initialized: {_keywords_cache_dir}")
except Exception as e:
    logger.error(f"❌ Failed to create keywords cache directory: {e}", exc_info=True)
_deepseek_llm = None

_keywords_cache_dir = Path("/tmp/keywords_cache")
_keywords_cache_ttl_minutes = 10


def _get_nlp():
    """Get or create spaCy NLP model for lemmatization (singleton)."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            model_names = ["es_core_news_sm", "es_core_news_md", "es_core_news_lg"]
            for model_name in model_names:
                try:
                    _nlp = spacy.load(model_name)
                    logger.info(f"✅ spaCy Spanish model loaded ({model_name})")
                    return _nlp
                except (OSError, IOError):
                    continue
            
            logger.warning("⚠️  No Spanish spaCy models found. Attempting to use blank Spanish model...")
            try:
                _nlp = spacy.blank("es")
                logger.info("✅ Using blank Spanish model (limited lemmatization)")
            except Exception:
                logger.warning("⚠️  Could not load blank Spanish model. Using basic tokenization.")
                _nlp = None
        except ImportError:
            logger.warning("⚠️  spacy not installed. Using basic tokenization without lemmatization")
            _nlp = None
    return _nlp


def _simple_stem_spanish(word: str) -> str:
    """
    Simple Spanish stemming without external libraries.
    Removes common suffixes to reduce word variations.
    
    Args:
        word: Word to stem
        
    Returns:
        Stemmed word
    """
    word_lower = word.lower()
    
    suffixes = [
        ("ísimos", ""), ("ísimas", ""), ("ísimo", ""), ("ísima", ""),
        ("os", ""), ("as", ""), ("es", ""), ("s", ""),
        ("ando", "ar"), ("iendo", "er"), ("iendo", "ir"),
        ("ado", "ar"), ("ido", "er"), ("ido", "ir"),
        ("ado", ""), ("ido", ""),
    ]
    
    for suffix, replacement in suffixes:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            return word_lower[:-len(suffix)] + replacement
    
    return word_lower


def _lemmatize_text(text: str) -> List[str]:
    """
    Lemmatize text to reduce words to their base form.
    Uses spaCy if available, otherwise uses simple stemming.
    
    Args:
        text: Text to lemmatize
        
    Returns:
        List of lemmatized words
    """
    nlp = _get_nlp()
    
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    if nlp is None:
        lemmas = [_simple_stem_spanish(word) for word in words if len(word) > 2]
        return lemmas
    
    try:
        doc = nlp(text_lower)
        lemmas = []
        for token in doc:
            if token.is_alpha and not token.is_stop and len(token.text) > 2:
                lemma = token.lemma_.lower()
                if lemma:
                    lemmas.append(lemma)
        return lemmas
    except Exception as e:
        logger.warning(f"⚠️  Error in spaCy lemmatization: {e}. Using simple stemming.")
        lemmas = [_simple_stem_spanish(word) for word in words if len(word) > 2]
        return lemmas


def _analyze_sentiment_bag_of_words(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment using bag of words approach with Spanish word dictionaries.
    Uses lemmatization to reduce words to their base form.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with label (POS/NEG/NEU) and probas (probabilities)
    """
    lemmas = _lemmatize_text(text)
    
    if len(lemmas) == 0:
        return {
            "output": "NEU",
            "probas": {"POS": 0.0, "NEG": 0.0, "NEU": 1.0}
        }
    
    positive_count = sum(1 for lemma in lemmas if lemma in POSITIVE_WORDS)
    negative_count = sum(1 for lemma in lemmas if lemma in NEGATIVE_WORDS)
    total_words = len(lemmas)
    
    positive_score = positive_count / total_words if total_words > 0 else 0
    negative_score = negative_count / total_words if total_words > 0 else 0
    
    if positive_score > negative_score and positive_score > 0.05:
        label = "POS"
        pos_prob = min(1.0, positive_score * 2)
        neg_prob = negative_score
        neu_prob = 1.0 - pos_prob - neg_prob
    elif negative_score > positive_score and negative_score > 0.05:
        label = "NEG"
        neg_prob = min(1.0, negative_score * 2)
        pos_prob = positive_score
        neu_prob = 1.0 - pos_prob - neg_prob
    else:
        label = "NEU"
        neu_prob = 0.7
        pos_prob = positive_score
        neg_prob = negative_score
    
    neu_prob = max(0.0, min(1.0, neu_prob))
    pos_prob = max(0.0, min(1.0, pos_prob))
    neg_prob = max(0.0, min(1.0, neg_prob))
    
    total_prob = pos_prob + neg_prob + neu_prob
    if total_prob > 0:
        pos_prob /= total_prob
        neg_prob /= total_prob
        neu_prob /= total_prob
    
    return {
        "output": label,
        "probas": {
            "POS": round(pos_prob, 3),
            "NEG": round(neg_prob, 3),
            "NEU": round(neu_prob, 3)
        }
    }


def _get_sentiment_analyzer():
    """Get or create sentiment analyzer (singleton) - uses bag of words."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = "bag_of_words"
        logger.info("✅ Sentiment analyzer initialized (bag of words - Spanish)")
    return _sentiment_analyzer


def count_keyword_mentions(keyword: str, id_company: int = 1) -> Dict[str, Any]:
    """
    Count how many posts contain the keyword in title or description.
    
    Args:
        keyword: Keyword to search for
        id_company: Company ID (default: 1)
        
    Returns:
        Dict with keyword and count_mentions
    """
    try:
        logger.info(f"🔍 Counting mentions for keyword: '{keyword}' (company: {id_company})")
        
        if not keyword or not keyword.strip():
            logger.warning("⚠️  Empty keyword provided")
            return {
                "keyword": keyword,
                "count_mentions": 0
            }
        
        keyword_clean = keyword.strip().lower()
        supabase = get_supabase_client()
        
        keyword_pattern = f"%{keyword_clean}%"
        
        query_title = supabase.table("posts").select("id").eq("id_company", id_company).ilike("title", keyword_pattern)
        response_title = query_title.execute()
        post_ids_title = {post["id"] for post in (response_title.data or [])}
        
        query_desc = supabase.table("posts").select("id").eq("id_company", id_company).ilike("description", keyword_pattern)
        response_desc = query_desc.execute()
        post_ids_desc = {post["id"] for post in (response_desc.data or [])}
        
        unique_post_ids = post_ids_title.union(post_ids_desc)
        count = len(unique_post_ids)
        
        logger.info(f"✅ Found {count} posts mentioning keyword '{keyword_clean}'")
        
        return {
            "keyword": keyword_clean,
            "count_mentions": count
        }
        
    except Exception as e:
        logger.error(f"❌ Error counting keyword mentions: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "keyword": keyword,
            "count_mentions": 0,
            "error": str(e)
        }


def calculate_sentiment_approval(keyword: Optional[str] = None, id_company: int = 1, limit: int = 1000) -> Dict[str, Any]:
    """
    Calculate sentiment approval (0-100) for posts.
    If keyword is provided, only analyzes posts containing that keyword.
    
    Args:
        keyword: Optional keyword to filter posts
        id_company: Company ID (default: 1)
        limit: Maximum number of posts to analyze
        
    Returns:
        Dict with approval_score (0-100), total_posts, positive_count, negative_count, neutral_count
    """
    try:
        logger.info(f"🔍 Calculating sentiment approval (keyword: {keyword}, company: {id_company})")
        
        analyzer = _get_sentiment_analyzer()
        if analyzer is None:
            return {
                "approval_score": 0,
                "total_posts": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "error": "Sentiment analyzer not available"
            }
        
        supabase = get_supabase_client()
        
        query = supabase.table("posts").select("id,title,description").eq("id_company", id_company)
        
        if keyword:
            keyword_clean = keyword.strip().lower()
            keyword_pattern = f"%{keyword_clean}%"
            query_title = supabase.table("posts").select("id,title,description").eq("id_company", id_company).ilike("title", keyword_pattern)
            query_desc = supabase.table("posts").select("id,title,description").eq("id_company", id_company).ilike("description", keyword_pattern)
            
            response_title = query_title.execute()
            response_desc = query_desc.execute()
            
            posts_title = {post["id"]: post for post in (response_title.data or [])}
            posts_desc = {post["id"]: post for post in (response_desc.data or [])}
            
            all_posts_dict = {**posts_title, **posts_desc}
            posts = list(all_posts_dict.values())[:limit]
        else:
            query = query.order("created_at", desc=True).limit(limit)
            response = query.execute()
            posts = response.data if response.data else []
        
        if len(posts) == 0:
            logger.warning(f"⚠️  No posts found for sentiment analysis")
            return {
                "approval_score": 0,
                "total_posts": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "keyword": keyword
            }
        
        logger.info(f"📊 Analyzing sentiment for {len(posts)} posts")
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_sentiment_score = 0.0
        
        for post in posts:
            text = ""
            if post.get("title"):
                text += post["title"] + " "
            if post.get("description"):
                text += post["description"]
            
            if not text.strip():
                continue
            
            try:
                if analyzer == "bag_of_words":
                    result = _analyze_sentiment_bag_of_words(text)
                else:
                    result = analyzer.predict(text)
                
                if isinstance(result, dict):
                    label = result.get("output", "NEU")
                    probs = result.get("probas", {})
                else:
                    label = result
                    probs = {}
                
                label_upper = str(label).upper()
                
                if "POS" in label_upper or "POSITIVE" in label_upper:
                    positive_count += 1
                    sentiment_value = 1.0
                elif "NEG" in label_upper or "NEGATIVE" in label_upper:
                    negative_count += 1
                    sentiment_value = -1.0
                else:
                    neutral_count += 1
                    sentiment_value = 0.0
                
                if probs:
                    pos_prob = probs.get("POS", probs.get("POSITIVE", 0))
                    neg_prob = probs.get("NEG", probs.get("NEGATIVE", 0))
                    neu_prob = probs.get("NEU", probs.get("NEUTRAL", 0))
                    
                    sentiment_value = (pos_prob * 1.0) + (neg_prob * -1.0) + (neu_prob * 0.0)
                
                total_sentiment_score += sentiment_value
                
            except Exception as e:
                logger.warning(f"⚠️  Error analyzing sentiment for post {post.get('id')}: {e}")
                continue
        
        total_analyzed = positive_count + negative_count + neutral_count
        
        if total_analyzed == 0:
            approval_score = 0
        else:
            average_sentiment = total_sentiment_score / total_analyzed
            approval_score = max(0, min(100, ((average_sentiment + 1.0) / 2.0) * 100))
        
        logger.info(f"✅ Sentiment analysis complete: approval={approval_score:.2f}% (pos: {positive_count}, neg: {negative_count}, neu: {neutral_count})")
        
        return {
            "approval_score": round(approval_score, 2),
            "total_posts": total_analyzed,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "keyword": keyword
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating sentiment approval: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "approval_score": 0,
            "total_posts": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "keyword": keyword,
            "error": str(e)
        }


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


def _get_keywords_cache_key(query: str, id_company: int) -> str:
    """Generate cache key for keywords."""
    key_string = f"{query.lower().strip()}|{id_company}"
    return hashlib.md5(key_string.encode()).hexdigest()


def _get_keywords_cache_file_path(cache_key: str) -> Path:
    """Get cache file path for keywords."""
    try:
        _keywords_cache_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return _keywords_cache_dir / f"{cache_key}.json"


def _load_keywords_cache(cache_key: str) -> Optional[List[str]]:
    """Load keywords from cache."""
    cache_file = _get_keywords_cache_file_path(cache_key)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        cached_time_str = cache_data.get('timestamp', '')
        if not cached_time_str:
            cache_file.unlink()
            return None
        
        cached_time = datetime.fromisoformat(cached_time_str)
        age = datetime.now() - cached_time
        
        if age > timedelta(minutes=_keywords_cache_ttl_minutes):
            logger.info(f"Keywords cache expired (age: {age.total_seconds()/60:.1f} min)")
            cache_file.unlink()
            return None
        
        keywords = cache_data.get('keywords', [])
        logger.info(f"✅✅✅ KEYWORDS CACHE HIT - Using cached topics (NO DEEPSEEK API CALLS)")
        return keywords
    except Exception as e:
        logger.warning(f"Error loading keywords cache: {e}")
        try:
            cache_file.unlink()
        except:
            pass
        return None


def _save_keywords_cache(cache_key: str, keywords: List[str]) -> None:
    """Save keywords to cache."""
    try:
        cache_file = _get_keywords_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'keywords': keywords
        }
        
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        temp_file.replace(cache_file)
        logger.info(f"✅ Saved keywords cache: {cache_key[:16]}...")
    except Exception as e:
        logger.error(f"Error saving keywords cache: {e}", exc_info=True)


def get_keywords(query: str, id_company: int = 1, limit: int = 100) -> Dict[str, Any]:
    """
    Obtener los últimos 50 posts, extraer títulos y usar agente DeepSeek para generar 5 tópicos de marketing.
    
    Args:
        query: Query para filtrar posts
        id_company: Company ID (default: 1)
        limit: Número máximo de posts a analizar (default: 50)
        
    Returns:
        Dict with query and keywords (lista de 5 tópicos cortos)
    """
    try:
        logger.info(f"🔍 Generating marketing topics from posts for query: '{query}' (company: {id_company})")
        
        if not query or not query.strip():
            logger.warning("⚠️  Empty query provided")
            return {
                "query": query,
                "keywords": []
            }
        
        query_clean = query.strip()
        cache_key = _get_keywords_cache_key(query_clean, id_company)
        
        cached_keywords = _load_keywords_cache(cache_key)
        if cached_keywords:
            return {
                "query": query_clean,
                "keywords": cached_keywords
            }
        
        logger.warning(f"❌❌❌ KEYWORDS CACHE MISS - Will make DeepSeek API call")
        
        supabase = get_supabase_client()
        
        keyword_pattern = f"%{query_clean.lower()}%"
        
        query_title = supabase.table("posts").select("id,title").eq("id_company", id_company).ilike("title", keyword_pattern)
        query_desc = supabase.table("posts").select("id,title").eq("id_company", id_company).ilike("description", keyword_pattern)
        
        response_title = query_title.execute()
        response_desc = query_desc.execute()
        
        posts_title = {post["id"]: post for post in (response_title.data or [])}
        posts_desc = {post["id"]: post for post in (response_desc.data or [])}
        
        all_posts_dict = {**posts_title, **posts_desc}
        posts = list(all_posts_dict.values())[:limit]
        
        if len(posts) == 0:
            logger.warning(f"⚠️  No posts found for query: '{query_clean}'")
            return {
                "query": query_clean,
                "keywords": []
            }
        
        logger.info(f"📊 Analyzing {len(posts)} posts for topic extraction")
        
        titles = []
        for post in posts:
            title = post.get("title", "")
            if title and title.strip():
                titles.append(title.strip())
        
        if len(titles) == 0:
            logger.warning("⚠️  No titles found in posts")
            return {
                "query": query_clean,
                "keywords": []
            }
        
        llm = _get_deepseek_llm()
        if not llm:
            logger.error("❌ DeepSeek LLM not available")
            return {
                "query": query_clean,
                "keywords": [],
                "error": "DeepSeek LLM not available"
            }
        
        titles_text = "\n".join([f"- {title}" for title in titles[:50]])
        
        prompt_text = f"""Eres un especialista en marketing digital y análisis de tendencias. Analiza los siguientes títulos de posts relacionados con "{query_clean}" y elabora 10 tópicos cortos (máximo 3-5 palabras cada uno) sobre lo que se está hablando la gente en esta data. Que de valor a la empresa incluye quejas, opiniones, etc.

TÍTULOS DE POSTS:
{titles_text}

INSTRUCCIONES:
- Analiza los títulos y identifica los temas principales que se están discutiendo
- Genera exactamente 10 tópicos cortos y concisos (máximo 3-5 palabras cada uno)
- Formato: ["tópico 1", "tópico 2", "tópico 3", "tópico 4", "tópico 5"]

Responde SOLO con el JSON array:"""
        
        logger.info(f"🤖 Calling DeepSeek agent to generate marketing topics...")
        response = llm.invoke(prompt_text)
        content = response.content.strip()
        
        logger.debug(f"Raw DeepSeek response: {content[:200]}...")
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        try:
            topics = json.loads(content)
            if not isinstance(topics, list):
                topics = []
            
            topics = topics[:5]
            
            _save_keywords_cache(cache_key, topics)
            
            logger.info(f"✅ Generated {len(topics)} marketing topics for query '{query_clean}'")
            
            return {
                "query": query_clean,
                "keywords": topics
            }
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}. Content: {content[:200]}")
            return {
                "query": query_clean,
                "keywords": [],
                "error": f"Error parsing agent response: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"❌ Error generating keywords: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "query": query,
            "keywords": [],
            "error": str(e)
        }

