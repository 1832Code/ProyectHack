from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
from decouple import config
from dotenv import load_dotenv
import psycopg2
from supabase import create_client, Client
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURACIÓN SUPABASE ====================
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect:{e}")


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
SUPABASE_URL = os.getenv('SUPABASE_URL', config('SUPABASE_URL', default=''))
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', config('SUPABASE_ANON_KEY', default=''))
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Cliente Supabase inicializado correctamente")
    except Exception as e:
        print(f"Error inicializando Supabase: {e}")

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

# ==================== MIDDLEWARE DE AUTENTICACIÓN ====================
def require_auth(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            user = supabase.auth.get_user(token)
            
            if not user:
                return jsonify({'error': 'Token inválido'}), 401
            
            request.user = user.user
            
        except Exception as e:
            print(f"Error verificando token: {e}")
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

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

def generate_final_results_with_ai(keyword_results, company_name, sector, country, external_data=None):
    """
    Genera resultados finales consolidados basados en todas las búsquedas y datos externos
    """
    external_context = ""
    if external_data:
        external_context = f"""
Información adicional de API externa:
Descripción: {external_data.get('description')}
Keywords sugeridos: {', '.join(external_data.get('suggested_keywords', []))}
"""

    prompt = f"""Basándote en los siguientes resultados de búsqueda de palabras clave y datos externos, 
genera un análisis consolidado para la empresa:

Empresa: {company_name}
Sector: {sector}
País: {country}
{external_context}

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
            response_text = response.split('```')[1]
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
def process_keywords(keyword_input, sector, country, suggested_keywords=None):
    """
    Procesa las palabras clave: analiza, busca en BD o ejecuta nueva búsqueda
    """
    # 1. Analizar y optimizar keywords con IA
    optimized_keywords = analyze_keywords_with_ai(keyword_input)
    
    # Agregar keywords sugeridos por el API externo si existen
    if suggested_keywords:
        # Combinar y eliminar duplicados
        optimized_keywords = list(set(optimized_keywords + suggested_keywords))
        # Limitar a un número razonable (ej. 8)
        optimized_keywords = optimized_keywords[:8]
    
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
            # Supabase devuelve dict, campo1 ya es JSON (dict) si es JSONB
            data_content = db_component['campo1']
            if isinstance(data_content, str):
                try:
                    data_content = json.loads(data_content)
                except:
                    pass
            
            results.append({
                'keyword': keyword,
                'source': 'database',
                'data': data_content
            })
        else:
            # 3.2 Verificar si es sinónimo de alguno existente
            if existing_keywords:
                synonym_check = check_synonym_with_ai(keyword, existing_keywords)
                
                if synonym_check['is_synonym'] and synonym_check['matched_word']:
                    # Usar el componente del sinónimo
                    synonym_component = get_component_from_db(synonym_check['matched_word'])
                    if synonym_component:
                        data_content = synonym_component['campo1']
                        if isinstance(data_content, str):
                            try:
                                data_content = json.loads(data_content)
                            except:
                                pass
                                
                        results.append({
                            'keyword': keyword,
                            'original_keyword': synonym_check['matched_word'],
                            'source': 'synonym',
                            'data': data_content
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
        'message': 'API de búsqueda empresarial con Supabase y Company Lookup'
    })

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================
@app.route('/auth/callback', methods=['POST'])
def auth_callback():
    """Recibe el token después del login y sincroniza con la BD"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Token no proporcionado'}), 400
        
        user = supabase.auth.get_user(access_token)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user_data = user.user
        
        # Verificar si el perfil existe
        profile = supabase.table('user_profiles')\
            .select('*')\
            .eq('id', user_data.id)\
            .execute()
        
        if not profile.data:
            # Crear perfil si no existe
            profile_data = {
                'id': user_data.id,
                'full_name': user_data.user_metadata.get('full_name', ''),
                'company_id': None
            }
            supabase.table('user_profiles').insert(profile_data).execute()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_data.id,
                'email': user_data.email,
                'full_name': user_data.user_metadata.get('full_name', '')
            }
        }), 200
        
    except Exception as e:
        print(f"Error en callback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/user', methods=['GET'])
@require_auth
def get_current_user():
    """Obtiene los datos del usuario actual"""
    try:
        user_id = request.user.id
        
        profile = supabase.table('user_profiles')\
            .select('*, companies(id, name, created_at)')\
            .eq('id', user_id)\
            .single()\
            .execute()
        
        return jsonify({
            'success': True,
            'user': profile.data
        }), 200
        
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Cierra sesión del usuario"""
    try:
        supabase.auth.sign_out()
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada correctamente'
        }), 200
        
    except Exception as e:
        print(f"Error en logout: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verifica si el token es válido"""
    return jsonify({
        'success': True,
        'user_id': request.user.id,
        'email': request.user.email
    }), 200

@app.route('/search', methods=['POST'])
@require_auth
def search():
    try:
        data = request.get_json()
        
        # Obtener ID del usuario autenticado
        user_id = request.user.id
        
        # Validar campos requeridos
        required_fields = ['name', 'country', 'sector', 'keyword']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        company_name = data['name']
        country = data['country']
        sector = data['sector']
        keyword_input = data['keyword']
        
        # 1. Consultar API externa de empresas
        print(f"Consultando API externa para: {company_name}")
        api_response = lookup_company(company_name, [keyword_input], country)
        external_data = extract_api_data(api_response)
        
        suggested_keywords = []
        if external_data:
            print("Datos externos encontrados")
            suggested_keywords = external_data.get('suggested_keywords', [])
        
        # 2. Procesar keywords (combinando input usuario + sugerencias API)
        keyword_results = process_keywords(keyword_input, sector, country, suggested_keywords)
        
        if not keyword_results:
            return jsonify({'error': 'No se pudieron procesar las palabras clave'}), 500
        
        # 3. Generar análisis final consolidado (incluyendo datos externos)
        final_results = generate_final_results_with_ai(
            keyword_results, 
            company_name, 
            sector, 
            country,
            external_data
        )
        
        # 4. Preparar respuesta
        response = {
            'company_name': company_name,
            'country': country,
            'sector': sector,
            'external_data': external_data,  # Incluir datos del API externo
            'keyword_analysis': keyword_results,
            'final_analysis': final_results,
            'timestamp': None
        }
        
        # 5. Crear la empresa en Supabase
        company_data = {
            'name': company_name,
            'country': country,
            'sector': sector,
            'keywords': {
                'original': keyword_input,
                'processed': [kr['keyword'] for kr in keyword_results],
                'suggested': suggested_keywords
            },
            'search_results': response
        }
        
        company_result = supabase.table('companies').insert(company_data).execute()
        
        company_id = None
        if company_result.data:
            company_id = company_result.data[0]['id']
            
            # Actualizar el perfil del usuario con esta empresa
            supabase.table('user_profiles')\
                .update({'company_id': company_id})\
                .eq('id', user_id)\
                .execute()
        
        # 6. Guardar en historial
        save_search_history(
            company_name, 
            country, 
            sector, 
            [kr['keyword'] for kr in keyword_results],
            response
        )
        
        return jsonify({
            'success': True,
            'company_id': company_id,
            'data': response
        }), 200
        
    except Exception as e:
        print(f"Error en endpoint /search: {e}")
        import traceback
        traceback.print_exc()
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