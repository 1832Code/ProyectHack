# 🚀 ProyectHack - Sistema de Búsqueda Empresarial

Sistema completo de búsqueda empresarial con IA, desarrollado para el Hackathon UNHEVAL.

## 📋 Descripción

Aplicación web full-stack que permite realizar búsquedas inteligentes de empresas utilizando IA (DeepSeek), con backend en Flask/FastAPI y frontend en Next.js.

## 🏗️ Estructura del Proyecto

```
ProyectHack/
├── backend/              # Backend Flask (Puerto 5000)
│   ├── main.py          # Servidor principal
│   ├── requirements.txt # Dependencias Python
│   ├── .env.example     # Ejemplo de configuración
│   ├── setup_database.sql # Script de BD
│   └── start.ps1        # Script de inicio rápido
│
├── hackathon/           # Backend FastAPI (Puerto 8000)
│   ├── requirements.txt
│   └── ...
│
├── frontend/            # Frontend Next.js (Puerto 3000)
│   ├── package.json
│   ├── start.ps1        # Script de inicio rápido
│   └── ...
│
└── INSTRUCCIONES_EJECUCION.md  # Guía completa
```

## ✅ Estado de Instalación

**¡Todas las dependencias han sido instaladas correctamente!**

### Backend (Flask)
- ✓ Flask 3.1.2
- ✓ flask-cors 6.0.1
- ✓ mysql-connector-python 9.5.0
- ✓ openai 2.8.1
- ✓ python-dotenv 1.2.1
- ✓ python-decouple 3.8

### Hackathon (FastAPI)
- ✓ apify-client
- ✓ fastapi
- ✓ uvicorn
- ✓ pydantic

### Frontend (Next.js)
- ✓ 185 paquetes instalados
- ✓ Next.js 16.0.3
- ✓ React 19.2.0

## 🔧 Configuración Inicial

### 1. Configurar Variables de Entorno

Crea el archivo `.env` en la carpeta `backend/`:

```bash
cd backend
copy .env.example .env
```

Edita el archivo `.env` y completa tus credenciales:

```env
DEEPSEEK_API_KEY=tu_clave_api_aqui
```

### 2. Configurar Base de Datos

1. Asegúrate de tener MySQL instalado y corriendo
2. Ejecuta el script de configuración:

```bash
mysql -u root -p < backend/setup_database.sql
```

O abre `backend/setup_database.sql` en MySQL Workbench y ejecútalo.

3. Actualiza las credenciales de BD en `backend/main.py` (líneas 22-27):

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'search_db',
    'user': 'root',
    'password': 'tu_password'  # ⚠️ Cambia esto
}
```

## 🚀 Inicio Rápido

### Opción 1: Scripts PowerShell (Recomendado para Windows)

**Backend:**
```powershell
cd backend
.\start.ps1
```

**Frontend:**
```powershell
cd frontend
.\start.ps1
```

### Opción 2: Comandos Manuales

**Backend Flask:**
```bash
cd backend
python main.py
```
Servidor en: http://localhost:5000

**Frontend Next.js:**
```bash
cd frontend
npm run dev
```
Servidor en: http://localhost:3000

**Hackathon FastAPI (Opcional):**
```bash
cd hackathon
uvicorn main:app --reload
```
Servidor en: http://localhost:8000

## 📡 Endpoints Disponibles

### Backend Flask (Puerto 5000)

- `GET /` - Estado del servidor
- `POST /search` - Búsqueda empresarial
  ```json
  {
    "name": "Nombre Empresa",
    "country": "País",
    "sector": "Sector",
    "keyword": "palabras clave de búsqueda"
  }
  ```
- `GET /results` - Obtener resultados

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask** 3.1.2 - Framework web
- **OpenAI** 2.8.1 - Integración con DeepSeek AI
- **MySQL Connector** 9.5.0 - Base de datos
- **Flask-CORS** 6.0.1 - CORS support
- **Python-Decouple** 3.8 - Gestión de configuración

### Frontend
- **Next.js** 16.0.3 - Framework React
- **React** 19.2.0 - Librería UI
- **Radix UI** - Componentes accesibles
- **Tailwind CSS** 4.1.9 - Estilos
- **TypeScript** 5 - Tipado estático

## 📦 Comandos Útiles

### Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import flask, flask_cors, mysql.connector, openai, decouple; print('✓ OK')"

# Ejecutar servidor
python main.py
```

### Frontend
```bash
# Instalar dependencias
npm install

# Modo desarrollo
npm run dev

# Build producción
npm run build

# Iniciar producción
npm start
```

## 🔍 Verificación de Instalación

Ejecuta estos comandos para verificar que todo esté instalado:

```bash
# Verificar Python
python --version

# Verificar Node.js
node --version

# Verificar dependencias backend
cd backend
python -c "import flask, flask_cors, mysql.connector, openai, decouple; print('✓ Backend OK')"

# Verificar dependencias frontend
cd frontend
npm list --depth=0
```

## ⚠️ Solución de Problemas

### Error: No se puede conectar a MySQL
- Verifica que MySQL esté corriendo
- Verifica las credenciales en `DB_CONFIG`
- Ejecuta el script `setup_database.sql`

### Error: DEEPSEEK_API_KEY no encontrada
- Verifica que el archivo `.env` exista en `backend/`
- Verifica que la variable esté correctamente configurada

### Error: Puerto en uso
- Cambia el puerto en el código o cierra la aplicación que lo está usando
- Backend Flask: Línea 428 en `main.py`
- Frontend: Usa `npm run dev -- -p 3001` para otro puerto

## 📝 Notas Importantes

1. **Entorno Virtual**: El proyecto incluye un entorno virtual en `.venv`
2. **Variables de Entorno**: Nunca subas el archivo `.env` a Git
3. **Base de Datos**: Asegúrate de crear las tablas antes de ejecutar
4. **API Keys**: Obtén tu clave de DeepSeek en https://platform.deepseek.com/

## 👥 Equipo

Proyecto desarrollado para el Hackathon UNHEVAL

## 📄 Licencia

Este proyecto es parte de un hackathon educativo.

---

## 🎯 Próximos Pasos

1. ✅ Instalar dependencias (COMPLETADO)
2. ⚠️ Configurar archivo `.env`
3. ⚠️ Configurar base de datos MySQL
4. ⚠️ Ejecutar backend
5. ⚠️ Ejecutar frontend
6. ⚠️ Probar la aplicación

---

**¿Necesitas ayuda?** Consulta el archivo `INSTRUCCIONES_EJECUCION.md` para más detalles.

¡Buena suerte con el hackathon! 🚀
