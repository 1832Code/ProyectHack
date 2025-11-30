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
│   ├── app/             # App Router (páginas y API routes)
│   ├── components/      # Componentes React reutilizables
│   ├── lib/             # Utilidades y configuración
│   ├── types/           # Definiciones TypeScript
│   ├── package.json     # Dependencias y scripts
│   └── start.sh         # Script de inicio
│
└── INSTRUCCIONES_EJECUCION.md  # Guía completa
```

---

## 🖥️ Frontend (Next.js) - Guía Completa

### Requisitos Previos

- **Node.js** >= 20.9.0
- **npm** >= 10.0.0 (o pnpm/bun como alternativa)

Verifica tu versión de Node.js:
```bash
node --version  # Debe ser v20.9.0 o superior
npm --version   # Debe ser v10.0.0 o superior
```

### Tecnologías Principales

| Tecnología | Versión | Descripción |
|------------|---------|-------------|
| Next.js | 16.0.3 | Framework React con App Router |
| React | 19.2.0 | Librería UI |
| TypeScript | 5.x | Tipado estático |
| Tailwind CSS | 4.x | Framework de estilos |
| NextAuth.js | 4.24.13 | Autenticación (Google OAuth) |
| Supabase | 2.86.0 | Base de datos y backend |
| Radix UI | - | Componentes accesibles |
| Motion | 12.x | Animaciones |

### Instalación del Frontend

1. **Navegar a la carpeta frontend:**
```bash
cd frontend
```

2. **Instalar dependencias:**

Con npm:
```bash
npm install
```

Con pnpm (alternativa):
```bash
pnpm install
```

Con bun (alternativa):
```bash
bun install
```

### Configuración de Variables de Entorno

Crea el archivo `.env.local` en la carpeta `frontend/`:

```bash
# En macOS/Linux
cp .env.example .env.local

# En Windows
copy .env.example .env.local
```

Configura las siguientes variables de entorno:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=tu-secret-aleatorio-seguro

# Google OAuth (obtener en Google Cloud Console)
GOOGLE_CLIENT_ID=tu-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-google-client-secret

# Supabase (obtener en tu proyecto de Supabase)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
SUPABASE_ANON_KEY=tu-anon-key
```

> 💡 **Tip:** Para generar un `NEXTAUTH_SECRET` seguro, ejecuta:
> ```bash
> openssl rand -base64 32
> ```

### Ejecutar el Frontend

#### Modo Desarrollo (con hot-reload)

```bash
npm run dev
```

El servidor estará disponible en: **http://localhost:3000**

Para usar un puerto diferente:
```bash
npm run dev -- -p 3001
```

#### Modo Producción

1. **Crear build de producción:**
```bash
npm run build
```

2. **Iniciar servidor de producción:**
```bash
npm start
```

O usar el script incluido:
```bash
./start.sh
```

### Scripts Disponibles

| Script | Comando | Descripción |
|--------|---------|-------------|
| dev | `npm run dev` | Servidor de desarrollo con hot-reload |
| build | `npm run build` | Crear build optimizado para producción |
| start | `npm start` | Iniciar servidor de producción |
| lint | `npm run lint` | Ejecutar ESLint |
| test | `npm test` | Ejecutar tests con Jest |
| test:watch | `npm run test:watch` | Tests en modo watch |

### Estructura de Carpetas del Frontend

```
frontend/
├── app/                    # App Router de Next.js
│   ├── api/               # API Routes
│   │   ├── analytics/     # Endpoint de analytics
│   │   ├── auth/          # NextAuth endpoints
│   │   ├── opportunity/   # Endpoint de oportunidades
│   │   ├── posts/         # Endpoint de posts
│   │   └── user-actions/  # Acciones de usuario
│   ├── buscar/            # Página de búsqueda
│   ├── claim/             # Página de claim
│   ├── dashboard/         # Dashboard principal
│   ├── signin/            # Página de login
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página de inicio
│   └── globals.css        # Estilos globales
│
├── components/            # Componentes React
│   ├── ui/               # Componentes UI base (shadcn/ui)
│   ├── dashboard/        # Componentes del dashboard
│   └── providers/        # Providers de contexto
│
├── lib/                   # Utilidades
│   ├── api.ts            # Cliente API
│   ├── auth.ts           # Configuración NextAuth
│   ├── supabase-server.ts # Cliente Supabase
│   └── utils.ts          # Funciones utilitarias
│
├── types/                 # Definiciones TypeScript
│   ├── analytics.ts
│   ├── company-lookup.ts
│   ├── company-posts.ts
│   └── opportunity.ts
│
└── public/               # Archivos estáticos
    └── logo.png
```

---

## ⚙️ Backend (Flask) - Configuración

### Configurar Variables de Entorno

Crea el archivo `.env` en la carpeta `backend/`:

```bash
cd backend
cp .env.example .env
```

Edita el archivo `.env` y completa tus credenciales:

```env
DEEPSEEK_API_KEY=tu_clave_api_aqui
```

### Configurar Base de Datos

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

---

## 🚀 Inicio Rápido - Todos los Servicios

### Opción 1: Scripts de Inicio

**Backend Flask:**
```bash
cd backend
# Windows
.\start.ps1

# macOS/Linux
python main.py
```

**Frontend Next.js:**
```bash
cd frontend
npm run dev
```

**Hackathon FastAPI (Opcional):**
```bash
cd hackathon
uvicorn main:app --reload
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

### Frontend API Routes (Puerto 3000)

- `GET /api/analytics` - Obtener analytics
- `GET /api/opportunity` - Obtener oportunidades
- `GET /api/posts` - Obtener posts de empresas
- `POST /api/user-actions` - Acciones de usuario
- `GET/POST /api/auth/*` - Autenticación NextAuth

---

## 🔍 Verificación de Instalación

Ejecuta estos comandos para verificar que todo esté instalado:

```bash
# Verificar Python
python --version

# Verificar Node.js (debe ser >= 20.9.0)
node --version

# Verificar npm (debe ser >= 10.0.0)
npm --version

# Verificar dependencias backend
cd backend
python -c "import flask, flask_cors, mysql.connector, openai, decouple; print('✓ Backend OK')"

# Verificar dependencias frontend
cd frontend
npm list --depth=0
```

---

## ⚠️ Solución de Problemas

### Frontend

#### Error: Node.js version incompatible
```bash
# El proyecto requiere Node.js >= 20.9.0
# Actualiza Node.js desde https://nodejs.org o usa nvm:
nvm install 20
nvm use 20
```

#### Error: Módulos no encontrados
```bash
# Limpia la caché e instala de nuevo
rm -rf node_modules
rm package-lock.json
npm install
```

#### Error: NEXTAUTH_SECRET no configurado
- Crea el archivo `.env.local` en `frontend/`
- Genera un secret seguro: `openssl rand -base64 32`

#### Error: Google OAuth no funciona
- Verifica `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` en `.env.local`
- Asegúrate de que `http://localhost:3000` esté en los URIs autorizados de Google Cloud Console

#### Error: Supabase connection failed
- Verifica `SUPABASE_URL` y las keys en `.env.local`
- Asegúrate de que el proyecto Supabase esté activo

#### Error: Puerto 3000 en uso
```bash
# Usar un puerto diferente
npm run dev -- -p 3001
```

### Backend

#### Error: No se puede conectar a MySQL
- Verifica que MySQL esté corriendo
- Verifica las credenciales en `DB_CONFIG`
- Ejecuta el script `setup_database.sql`

#### Error: DEEPSEEK_API_KEY no encontrada
- Verifica que el archivo `.env` exista en `backend/`
- Verifica que la variable esté correctamente configurada

#### Error: Puerto 5000 en uso
- Cambia el puerto en la línea 428 de `main.py`

---

## 📝 Notas Importantes

1. **Node.js**: El frontend requiere Node.js >= 20.9.0
2. **Variables de Entorno**: Nunca subas `.env` o `.env.local` a Git
3. **Base de Datos**: Configura Supabase para el frontend y MySQL para el backend
4. **API Keys**: 
   - DeepSeek: https://platform.deepseek.com/
   - Google OAuth: https://console.cloud.google.com/
   - Supabase: https://supabase.com/dashboard

---

## 👥 Equipo

Proyecto desarrollado para el Hackathon UNHEVAL

## 📄 Licencia

Este proyecto es parte de un hackathon educativo.

---

## 🎯 Checklist de Configuración

### Frontend
- [ ] Node.js >= 20.9.0 instalado
- [ ] Dependencias instaladas (`npm install`)
- [ ] Archivo `.env.local` creado
- [ ] `NEXTAUTH_SECRET` configurado
- [ ] Google OAuth configurado (opcional)
- [ ] Supabase configurado
- [ ] `npm run dev` ejecutándose en http://localhost:3000

### Backend
- [ ] Python instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` creado
- [ ] `DEEPSEEK_API_KEY` configurado
- [ ] MySQL configurado y corriendo
- [ ] `python main.py` ejecutándose en http://localhost:5000

---

**¿Necesitas ayuda?** Consulta el archivo `INSTRUCCIONES_EJECUCION.md` para más detalles.

¡Buena suerte con el hackathon! 🚀
