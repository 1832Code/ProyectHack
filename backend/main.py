from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
from decouple import config
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURACIÓN ====================
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', config('DEEPSEEK_API_KEY'))
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ==================== SUPABASE CONFIGURATION ====================
# Configuración para conexión con Supabase
# Las credenciales deben estar en el archivo .env
# Descomenta y configura cuando tengas las credenciales listas
# SUPABASE_URL = os.getenv('SUPABASE_URL', config('SUPABASE_URL', default=''))
# SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', config('SUPABASE_ANON_KEY', default=''))
# supabase: Client = None
# if SUPABASE_URL and SUPABASE_KEY:
#     try:
#         supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#         print("Cliente Supabase inicializado correctamente")
#     except Exception as e:
#         print(f"Error inicializando Supabase: {e}")

# Configuración de Base de Datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'search_db',
    'user': 'root',
    'password': 'tu_password'
}

# ==================== CONEXIÓN BD ====================
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error conectando a BD: {e}")
        return None

# ==================== FUNCIONES DE IA ====================
def analyze_keywords_with_ai(keyword_input):
    """
    Analiza el input del usuario y descompone en palabras clave optimizadas
    """
    prompt = f"""Analiza el siguiente input del usuario y descompónlo en palabras clave concisas y optimizadas:

Input: "{keyword_input}"

Reglas:
1. Descompón en palabras individuales (no oraciones)
2. Elimina redundancias y sinónimos (elige la palabra con más impacto)
3. Máximo 5 palabras clave
4. Retorna SOLO un JSON con este formato exacto:
{{"keywords": ["palabra1", "palabra2", "palabra3"]}}

No agregues texto adicional, solo el JSON."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        # Limpia posibles markdown
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        result = json.loads(response_text)
        return result.get('keywords', [])
    except Exception as e:
        print(f"Error en análisis de keywords: {e}")
        return []

def check_synonym_with_ai(word, component_words):
    """
    Verifica si una palabra es sinónima de alguna en la lista de componentes
    """
    prompt = f"""¿La palabra "{word}" es sinónima o muy similar a alguna de estas palabras?
Lista: {', '.join(component_words)}

Retorna SOLO un JSON con este formato exacto:
{{"is_synonym": true/false, "matched_word": "palabra_coincidente_o_null"}}

Si no hay sinónimo, matched_word debe ser null."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"Error verificando sinónimos: {e}")
        return {"is_synonym": False, "matched_word": None}

def search_with_ai(keyword, sector, country):
    """
    Realiza búsqueda con IA para una palabra clave específica
    """
    prompt = f"""Busca información relevante sobre empresas con las siguientes características:
- Palabra clave: {keyword}
- Sector: {sector}
- País: {country}

Proporciona información general sobre empresas que coincidan con estos criterios.
Retorna SOLO un JSON con este formato:
{{"keyword": "{keyword}", "description": "descripción breve", "relevance_score": 0-100}}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Error en búsqueda con IA: {e}")
        return None

def generate_final_results_with_ai(keyword_results, company_name, sector, country):
    """
    Genera resultados finales consolidados basados en todas las búsquedas
    """
    prompt = f"""Basándote en los siguientes resultados de búsqueda de palabras clave, 
genera un análisis consolidado para la empresa:

Empresa: {company_name}
Sector: {sector}
País: {country}

Resultados de palabras clave:
{json.dumps(keyword_results, indent=2)}

Genera un análisis general y recomendaciones. Retorna SOLO un JSON con este formato:
{{
  "summary": "resumen general",
  "key_findings": ["hallazgo1", "hallazgo2"],
  "recommendations": ["recomendación1", "recomendación2"],
  "overall_score": 0-100
}}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Error generando resultados finales: {e}")
        return None

# ==================== FUNCIONES DE BD ====================
def get_component_from_db(keyword):
    """
    Busca una palabra clave en la tabla de componentes
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM components WHERE keyword = %s"
        cursor.execute(query, (keyword.lower(),))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Error consultando BD: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_component_keywords():
    """
    Obtiene todas las palabras clave registradas en componentes
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = "SELECT keyword FROM components"
        cursor.execute(query)
        results = cursor.fetchall()
        return [row[0] for row in results]
    except Error as e:
        print(f"Error consultando BD: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def save_component_to_db(keyword, result_data):
    """
    Guarda un nuevo componente en la BD
    Estructura flexible: keyword, campo1, campo2, campo3, campo4
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """INSERT INTO components 
                   (keyword, campo1, campo2, campo3, campo4) 
                   VALUES (%s, %s, %s, %s, %s)"""
        
        # Ajusta según los campos que decidas usar
        values = (
            keyword.lower(),
            json.dumps(result_data),  # campo1: resultado completo
            result_data.get('description', ''),  # campo2: descripción
            result_data.get('relevance_score', 0),  # campo3: score
            None  # campo4: por definir
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
    except Error as e:
        print(f"Error guardando en BD: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_search_history(company_name, country, sector, keywords, results):
    """
    Guarda el historial de búsqueda
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """INSERT INTO search_history 
                   (company_name, country, sector, keywords, results, created_at) 
                   VALUES (%s, %s, %s, %s, %s, NOW())"""
        
        values = (
            company_name,
            country,
            sector,
            json.dumps(keywords),
            json.dumps(results)
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
    except Error as e:
        print(f"Error guardando historial: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# ==================== LÓGICA PRINCIPAL ====================
def process_keywords(keyword_input, sector, country):
    """
    Procesa las palabras clave: analiza, busca en BD o ejecuta nueva búsqueda
    """
    # 1. Analizar y optimizar keywords con IA
    optimized_keywords = analyze_keywords_with_ai(keyword_input)
    
    if not optimized_keywords:
        return []
    
    # 2. Obtener lista de componentes existentes
    existing_keywords = get_all_component_keywords()
    
    results = []
    
    # 3. Procesar cada keyword optimizada
    for keyword in optimized_keywords:
        # 3.1 Verificar si ya existe en BD
        db_component = get_component_from_db(keyword)
        
        if db_component:
            # Ya existe, usar datos guardados
            results.append({
                'keyword': keyword,
                'source': 'database',
                'data': json.loads(db_component['campo1'])
            })
        else:
            # 3.2 Verificar si es sinónimo de alguno existente
            if existing_keywords:
                synonym_check = check_synonym_with_ai(keyword, existing_keywords)
                
                if synonym_check['is_synonym'] and synonym_check['matched_word']:
                    # Usar el componente del sinónimo
                    synonym_component = get_component_from_db(synonym_check['matched_word'])
                    if synonym_component:
                        results.append({
                            'keyword': keyword,
                            'original_keyword': synonym_check['matched_word'],
                            'source': 'synonym',
                            'data': json.loads(synonym_component['campo1'])
                        })
                        continue
            
            # 3.3 No existe y no tiene sinónimo: hacer nueva búsqueda
            search_result = search_with_ai(keyword, sector, country)
            
            if search_result:
                # Guardar en BD para futuras búsquedas
                save_component_to_db(keyword, search_result)
                
                results.append({
                    'keyword': keyword,
                    'source': 'new_search',
                    'data': search_result
                })
    
    return results

# ==================== ENDPOINTS ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'API de búsqueda empresarial'
    })

@app.route('/search', methods=['POST'])
def search():
    """
    Endpoint principal de búsqueda
    Recibe: name, country, sector, keyword
    Retorna: resultados procesados
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['name', 'country', 'sector', 'keyword']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        company_name = data['name']
        country = data['country']
        sector = data['sector']
        keyword_input = data['keyword']
        
        # Procesar keywords
        keyword_results = process_keywords(keyword_input, sector, country)
        
        if not keyword_results:
            return jsonify({'error': 'No se pudieron procesar las palabras clave'}), 500
        
        # Generar análisis final consolidado
        final_results = generate_final_results_with_ai(
            keyword_results, 
            company_name, 
            sector, 
            country
        )
        
        # Preparar respuesta
        response = {
            'company_name': company_name,
            'country': country,
            'sector': sector,
            'keyword_analysis': keyword_results,
            'final_analysis': final_results,
            'timestamp': None  # Se puede agregar timestamp
        }
        
        # Guardar en historial
        save_search_history(
            company_name, 
            country, 
            sector, 
            [kr['keyword'] for kr in keyword_results],
            response
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error en endpoint /search: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/results', methods=['GET'])
def results():
    """
    Endpoint para obtener resultados guardados (opcional)
    """
    return jsonify({'message': 'Endpoint de resultados'}), 200

# ==================== INICIALIZACIÓN ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)