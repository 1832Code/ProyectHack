# 🚀 Instrucciones de Ejecución del Proyecto

## ✅ Estado de Instalación

Todas las dependencias han sido instaladas correctamente:

### Backend (Flask)
- ✓ Flask 3.1.2
- ✓ flask-cors 6.0.1
- ✓ mysql-connector-python 9.5.0
- ✓ openai 2.8.1
- ✓ python-dotenv 1.2.1
- ✓ python-decouple 3.8

### Hackathon (FastAPI)
- ✓ apify-client >=1.0.0
- ✓ python-dotenv >=1.0.0
- ✓ fastapi >=0.104.0
- ✓ uvicorn[standard] >=0.24.0
- ✓ pydantic >=2.0.0

### Frontend (Next.js)
- ✓ 185 paquetes instalados
- ✓ Next.js 16.0.3
- ✓ React 19.2.0
- ✓ Todas las dependencias de Radix UI y componentes

---

## 🔧 Configuración Necesaria

### 1. Backend - Archivo `.env`

Antes de ejecutar el backend, asegúrate de tener el archivo `.env` en la carpeta `backend` con las siguientes variables:

```env
DEEPSEEK_API_KEY=tu_clave_api_aqui
```

### 2. Base de Datos MySQL

El backend requiere una base de datos MySQL configurada. Verifica la configuración en `backend/main.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'search_db',
    'user': 'root',
    'password': 'tu_password'  # ⚠️ Cambia esto por tu contraseña
}
```

**Tablas necesarias:**
- `components` - Para almacenar componentes de búsqueda
- `search_history` - Para el historial de búsquedas

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción 1: Ejecutar Backend (Flask)

```bash
cd backend
python main.py
```

El servidor Flask se ejecutará en: `http://localhost:5000`

### Opción 2: Ejecutar Hackathon (FastAPI)

```bash
cd hackathon
uvicorn main:app --reload
```

El servidor FastAPI se ejecutará en: `http://localhost:8000`

### Opción 3: Ejecutar Frontend (Next.js)

```bash
cd frontend
npm run dev
```

El frontend se ejecutará en: `http://localhost:3000`

---

## 📋 Ejecutar Todo el Proyecto

Para ejecutar el proyecto completo, necesitas abrir **3 terminales**:

### Terminal 1 - Backend
```bash
cd backend
python main.py
```

### Terminal 2 - Hackathon (opcional)
```bash
cd hackathon
uvicorn main:app --reload
```

### Terminal 3 - Frontend
```bash
cd frontend
npm run dev
```

---

## 🔍 Verificación de Instalación

### Verificar Backend
```bash
cd backend
python -c "import flask, flask_cors, mysql.connector, openai, decouple; print('✓ OK')"
```

### Verificar Frontend
```bash
cd frontend
npm list --depth=0
```

---

## ⚠️ Problemas Comunes

### 1. Error de Base de Datos
Si obtienes un error de conexión a MySQL:
- Verifica que MySQL esté corriendo
- Verifica las credenciales en `DB_CONFIG`
- Crea la base de datos: `CREATE DATABASE search_db;`

### 2. Error de API Key
Si obtienes un error de API:
- Verifica que el archivo `.env` exista en `backend/`
- Verifica que `DEEPSEEK_API_KEY` esté configurada correctamente

### 3. Error en Frontend
Si el frontend no inicia:
- Ejecuta `npm install` nuevamente en la carpeta `frontend`
- Verifica que Node.js versión 22+ esté instalado

---

## 📦 Versiones Instaladas

- **Python**: 3.14.0
- **Node.js**: v22.21.0
- **pip**: Última versión
- **npm**: Última versión

---

## 🎯 Endpoints Disponibles

### Backend (Flask) - Puerto 5000
- `GET /` - Estado del servidor
- `POST /search` - Búsqueda empresarial
- `GET /results` - Obtener resultados

### Frontend - Puerto 3000
- Interfaz de usuario completa

---

## 📝 Notas Adicionales

1. **Entorno Virtual**: El proyecto tiene un entorno virtual en `.venv` (si lo usas, actívalo primero)
2. **Variables de Entorno**: Asegúrate de configurar todas las variables necesarias
3. **Base de Datos**: Crea las tablas necesarias antes de ejecutar el backend

---

¡Todo está listo para ejecutar! 🎉
