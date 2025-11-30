"""
Analytics Module
Author: Mauricio J. @synaw_w
"""

import logging
import re
from typing import Optional, Dict, Any, List
from src.modules.supabase_connection import get_supabase_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_sentiment_analyzer = None
_nlp = None


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

POSITIVE_WORDS = {
    "bueno", "excelente", "genial", "fantástico", "maravilloso", "perfecto", "increíble",
    "amor", "adorar", "encantar", "feliz", "alegre", "satisfecho", "contento",
    "satisfacción", "recomendar", "recomendado", "recomendable", "mejor", "superior",
    "delicioso", "rico", "sabroso", "exquisito", "divino", "espectacular", "magnífico",
    "estupendo", "fabuloso", "sorprendente", "extraordinario", "brillante", "ideal",
    "óptimo", "satisfactorio", "agradable", "placentero", "disfrutar", "volver",
    "gustar", "favorito", "preferido", "destacado", "notable", "sobresaliente",
    "excepcional", "único", "especial", "impresionante", "asombroso", "radiante",
    "espléndido", "luminoso"
}

NEGATIVE_WORDS = {
    "malo", "mala", "malos", "malas", "terrible", "horrible", "pésimo", "pésima",
    "pésimos", "pésimas", "decepcionante", "decepcionantes", "mal", "malísimo",
    "malísima", "malísimos", "malísimas", "asqueroso", "asquerosa", "asquerosos",
    "asquerosas", "repugnante", "repugnantes", "desagradable", "desagradables",
    "odio", "odiar", "odio", "odiamos", "odiarás", "triste", "tristes", "tristeza",
    "deprimido", "deprimida", "deprimidos", "deprimidas", "frustrado", "frustrada",
    "frustrados", "frustradas", "enojado", "enojada", "enojados", "enojadas",
    "molesto", "molesta", "molestos", "molestas", "irritado", "irritada",
    "irritados", "irritadas", "furioso", "furiosa", "furiosos", "furiosas",
    "disgustado", "disgustada", "disgustados", "disgustadas", "descontento",
    "descontenta", "descontentos", "descontentas", "insatisfecho", "insatisfecha",
    "insatisfechos", "insatisfechas", "decepcionado", "decepcionada", "decepcionados",
    "decepcionadas", "desilusionado", "desilusionada", "desilusionados",
    "desilusionadas", "desesperado", "desesperada", "desesperados", "desesperadas",
    "desesperanzado", "desesperanzada", "desesperanzados", "desesperanzadas",
    "desalentado", "desalentada", "desalentados", "desalentadas", "desanimado",
    "desanimada", "desanimados", "desanimadas", "desmotivado", "desmotivada",
    "desmotivados", "desmotivadas", "desalentado", "desalentada", "desalentados",
    "desalentadas", "desilusionado", "desilusionada", "desilusionados",
    "desilusionadas", "decepcionado", "decepcionada", "decepcionados",
    "decepcionadas", "insatisfecho", "insatisfecha", "insatisfechos",
    "insatisfechas", "descontento", "descontenta", "descontentos", "descontentas",
    "molesto", "molesta", "molestos", "molestas", "irritado", "irritada",
    "irritados", "irritadas", "furioso", "furiosa", "furiosos", "furiosas",
    "enojado", "enojada", "enojados", "enojadas", "disgustado", "disgustada",
    "disgustados", "disgustadas", "repugnante", "repugnantes", "asqueroso",
    "asquerosa", "asquerosos", "asquerosas", "desagradable", "desagradables",
    "horrible", "horribles", "terrible", "terribles", "pésimo", "pésima",
    "pésimos", "pésimas", "malo", "mala", "malos", "malas", "mal", "malísimo",
    "malísima", "malísimos", "malísimas", "decepcionante", "decepcionantes",
    "desastroso", "desastrosa", "desastrosos", "desastrosas", "catastrófico",
    "catastrófica", "catastróficos", "catastróficas", "devastador", "devastadora",
    "devastadores", "devastadoras", "destructivo", "destructiva", "destructivos",
    "destructivas", "perjudicial", "perjudiciales", "dañino", "dañina", "dañinos",
    "dañinas", "nocivo", "nociva", "nocivos", "nocivas", "tóxico", "tóxica",
    "tóxicos", "tóxicas", "venenoso", "venenosa", "venenosos", "venenosas",
    "peligroso", "peligrosa", "peligrosos", "peligrosas", "riesgoso", "riesgosa",
    "riesgosos", "riesgosas", "arriesgado", "arriesgada", "arriesgados",
    "arriesgadas", "inseguro", "insegura", "inseguros", "inseguras", "inestable",
    "inestables", "inconstante", "inconstantes", "variable", "variables",
    "impredecible", "impredecibles", "imprevisible", "imprevisibles",
    "inesperado", "inesperada", "inesperados", "inesperadas", "sorpresivo",
    "sorpresiva", "sorpresivos", "sorpresivas", "inesperado", "inesperada",
    "inesperados", "inesperadas", "sorpresivo", "sorpresiva", "sorpresivos",
    "sorpresivas", "inesperado", "inesperada", "inesperados", "inesperadas"
}


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
        
        keyword_clean = keyword.strip()
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
            keyword_pattern = f"%{keyword.strip()}%"
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

