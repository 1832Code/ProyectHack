# 🔍 Análisis de Conflictos: Frontend vs Backend

## 📊 Resumen Ejecutivo

**Estado**: ⚠️ **CONFLICTOS CRÍTICOS DETECTADOS**

El frontend y el backend **NO están integrados**. El frontend es completamente estático con datos hardcodeados, mientras que el backend tiene una API funcional que no está siendo utilizada.

---

## 🏗️ Estructura Actual

### Frontend (Next.js)
```
frontend/
├── app/
│   ├── page.tsx           → SplashScreen (pantalla inicial)
│   ├── buscar/page.tsx    → SearchScreen (formulario de búsqueda)
│   └── dashboard/page.tsx → DashboardScreen (resultados)
└── components/
    ├── splash-screen.tsx
    ├── search-screen.tsx   → ⚠️ NO hace llamadas al backend
    └── dashboard-screen.tsx → ⚠️ Datos hardcodeados
```

### Backend (Flask)
```
backend/
└── main.py
    ├── POST /search       → API funcional
    ├── GET /results       → Endpoint disponible
    └── GET /              → Health check
```

---

## 🚨 CONFLICTOS CRÍTICOS

### 1. **NO HAY INTEGRACIÓN API** ⛔

**Problema**: El formulario de búsqueda NO envía datos al backend.

**Código Actual** (`search-screen.tsx` líneas 48-54):
```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  
  if (!validate()) return
  
  router.push("/dashboard")  // ⚠️ Solo redirige, NO envía datos
}
```

**Lo que debería hacer**:
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  
  if (!validate()) return
  
  // ✅ Enviar datos al backend
  const response = await fetch('http://localhost:5000/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: companyName,
      country: country,
      sector: 'Technology', // Falta este campo en el formulario
      keyword: keywords
    })
  })
  
  const data = await response.json()
  // Guardar datos y redirigir
  router.push("/dashboard")
}
```

---

### 2. **DATOS HARDCODEADOS EN DASHBOARD** ⛔

**Problema**: El dashboard muestra datos estáticos de "Rappi" en lugar de datos reales del backend.

**Código Actual** (`dashboard-screen.tsx`):
```typescript
// Líneas 79-380: Array hardcodeado con 30 menciones de Rappi
const allMentions = [
  {
    id: 1,
    platform: "tiktok",
    username: "@delivery_fails",
    content: "POV: When Rappi says 10 minutes...",
    // ... más datos estáticos
  },
  // ... 29 menciones más hardcodeadas
]
```

**Datos mostrados**:
- Empresa: "Rappi" (hardcodeado)
- País: "Peru" (hardcodeado)
- Menciones: 32k (hardcodeado)
- Aprobación: 89% (hardcodeado)
- Todas las menciones sociales son datos de ejemplo

---

### 3. **FALTA CAMPO "SECTOR" EN FORMULARIO** ⚠️

**Problema**: El backend requiere 4 campos, pero el frontend solo captura 3.

**Backend requiere** (`main.py` líneas 370-373):
```python
required_fields = ['name', 'country', 'sector', 'keyword']
```

**Frontend captura** (`search-screen.tsx`):
```typescript
const [companyName, setCompanyName] = useState("")  // ✅ name
const [country, setCountry] = useState("")          // ✅ country
const [keywords, setKeywords] = useState("")        // ✅ keyword
// ❌ FALTA: sector
```

---

### 4. **INCOMPATIBILIDAD EN FORMATO DE PAÍS** ⚠️

**Frontend** (`search-screen.tsx` líneas 15-18):
```typescript
const countries = [
  { id: "peru", label: "Peru" },    // Envía: "peru" (minúscula)
  { id: "chile", label: "Chile" },  // Envía: "chile" (minúscula)
]
```

**Backend espera**: Probablemente "Peru" o "Chile" (capitalizado), pero no hay validación explícita.

---

### 5. **NO HAY MANEJO DE ESTADOS DE CARGA** ⚠️

**Problema**: El frontend no muestra estados de carga mientras espera la respuesta del backend.

**Código Actual**:
```typescript
const [isSubmitting, setIsSubmitting] = useState(false)
// ⚠️ Variable declarada pero NUNCA usada
```

---

### 6. **NO HAY MANEJO DE ERRORES** ⚠️

**Problema**: Si el backend falla, el usuario no recibe ningún feedback.

**Falta**:
- Try/catch para errores de red
- Validación de respuesta del backend
- Mensajes de error al usuario
- Manejo de timeout

---

### 7. **FALTA CONFIGURACIÓN DE CORS** ⚠️

**Estado Actual**: El backend tiene CORS habilitado (`flask-cors`), pero no hay configuración específica.

**Código Backend** (`main.py` líneas 10-11):
```python
app = Flask(__name__)
CORS(app)  # ✅ CORS habilitado globalmente
```

**Potencial problema**: Si el frontend corre en un puerto diferente, podría haber problemas de CORS si no está bien configurado.

---

## 📋 ESTRUCTURA DE DATOS

### Backend Espera (POST /search)
```json
{
  "name": "string",      // Nombre de la empresa
  "country": "string",   // País
  "sector": "string",    // Sector (REQUERIDO pero falta en frontend)
  "keyword": "string"    // Palabras clave
}
```

### Backend Retorna
```json
{
  "company_name": "string",
  "country": "string",
  "sector": "string",
  "keyword_analysis": [
    {
      "keyword": "string",
      "source": "database|synonym|new_search",
      "data": {
        "keyword": "string",
        "description": "string",
        "relevance_score": 0-100
      }
    }
  ],
  "final_analysis": {
    "summary": "string",
    "key_findings": ["string"],
    "recommendations": ["string"],
    "overall_score": 0-100
  },
  "timestamp": null
}
```

### Frontend Necesita Mostrar
- ✅ Nombre de empresa (tiene UI)
- ✅ País (tiene UI)
- ❌ Análisis de keywords (NO implementado)
- ❌ Summary/findings (NO implementado)
- ❌ Recommendations (NO implementado)
- ❌ Overall score (NO implementado)

---

## 🔧 SOLUCIONES REQUERIDAS

### Prioridad ALTA 🔴

#### 1. **Integrar API en SearchScreen**
- Agregar llamada fetch al backend
- Manejar estados de carga
- Implementar manejo de errores
- Guardar respuesta para el dashboard

#### 2. **Agregar Campo "Sector" al Formulario**
- Agregar selector de sector en `search-screen.tsx`
- Opciones sugeridas: Technology, Food, Retail, Services, etc.

#### 3. **Conectar Dashboard con Datos Reales**
- Recibir datos del backend
- Reemplazar datos hardcodeados
- Mostrar análisis real de la IA

### Prioridad MEDIA 🟡

#### 4. **Estandarizar Formato de Datos**
- Decidir formato de país (minúscula vs capitalizado)
- Validar en backend

#### 5. **Implementar Gestión de Estado**
- Usar Context API o Zustand para compartir datos entre páginas
- Almacenar resultados de búsqueda

#### 6. **Mejorar UX**
- Loading states
- Error messages
- Success feedback

### Prioridad BAJA 🟢

#### 7. **Optimizaciones**
- Caché de resultados
- Validación de formularios mejorada
- Retry logic para fallos de red

---

## 📊 COMPARACIÓN: ESPERADO vs ACTUAL

| Aspecto | Backend Ofrece | Frontend Usa | Estado |
|---------|---------------|--------------|--------|
| Búsqueda con IA | ✅ Implementado | ❌ No integrado | 🔴 CRÍTICO |
| Análisis de keywords | ✅ Implementado | ❌ No mostrado | 🔴 CRÍTICO |
| Base de datos | ✅ Configurado | ❌ No usado | 🔴 CRÍTICO |
| Historial | ✅ Guardado | ❌ No accesible | 🟡 MEDIO |
| Sinónimos IA | ✅ Implementado | ❌ No usado | 🟡 MEDIO |
| Campo Sector | ✅ Requerido | ❌ No existe | 🔴 CRÍTICO |

---

## 🎯 PLAN DE ACCIÓN RECOMENDADO

### Fase 1: Integración Básica (2-3 horas)
1. ✅ Agregar campo "sector" al formulario
2. ✅ Implementar llamada API en `handleSubmit`
3. ✅ Crear servicio API (`lib/api.ts`)
4. ✅ Implementar Context para compartir datos

### Fase 2: Dashboard Dinámico (3-4 horas)
1. ✅ Recibir datos del backend en dashboard
2. ✅ Mapear datos de IA a componentes UI
3. ✅ Reemplazar datos hardcodeados
4. ✅ Implementar estados de carga

### Fase 3: Mejoras UX (2-3 horas)
1. ✅ Manejo de errores
2. ✅ Validaciones mejoradas
3. ✅ Feedback visual
4. ✅ Loading states

---

## 🚀 CÓDIGO DE EJEMPLO PARA INTEGRACIÓN

### 1. Crear servicio API (`frontend/lib/api.ts`)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

export interface SearchRequest {
  name: string
  country: string
  sector: string
  keyword: string
}

export interface SearchResponse {
  company_name: string
  country: string
  sector: string
  keyword_analysis: Array<{
    keyword: string
    source: string
    data: any
  }>
  final_analysis: {
    summary: string
    key_findings: string[]
    recommendations: string[]
    overall_score: number
  }
  timestamp: string | null
}

export async function searchCompany(data: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }

  return response.json()
}
```

### 2. Actualizar SearchScreen

```typescript
// Agregar imports
import { searchCompany } from '@/lib/api'
import { useRouter } from 'next/navigation'

// Agregar estado para sector
const [sector, setSector] = useState("")

// Actualizar handleSubmit
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  
  if (!validate()) return
  
  setIsSubmitting(true)
  
  try {
    const result = await searchCompany({
      name: companyName,
      country: country,
      sector: sector,
      keyword: keywords
    })
    
    // Guardar resultado en localStorage o Context
    localStorage.setItem('searchResult', JSON.stringify(result))
    
    router.push('/dashboard')
  } catch (error) {
    console.error('Search failed:', error)
    // Mostrar error al usuario
  } finally {
    setIsSubmitting(false)
  }
}
```

### 3. Agregar campo Sector al formulario

```typescript
// Agregar después del campo country
<div className="flex flex-col gap-2">
  <Label className="text-base text-muted-foreground italic font-normal">
    sector
  </Label>
  <select
    value={sector}
    onChange={(e) => setSector(e.target.value)}
    className="h-14 px-4 bg-card border-0 rounded-2xl text-base"
  >
    <option value="">Select sector</option>
    <option value="Technology">Technology</option>
    <option value="Food">Food & Beverage</option>
    <option value="Retail">Retail</option>
    <option value="Services">Services</option>
    <option value="Finance">Finance</option>
  </select>
</div>
```

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### Base de Datos
El backend requiere MySQL configurado. Asegúrate de:
1. ✅ Ejecutar `setup_database.sql`
2. ✅ Configurar credenciales en `main.py`
3. ✅ Verificar que MySQL esté corriendo

### API Key
El backend requiere `DEEPSEEK_API_KEY`:
1. ✅ Crear archivo `.env` en `backend/`
2. ✅ Agregar tu API key
3. ✅ Verificar que se carga correctamente

### CORS
Si hay problemas de CORS:
```python
# En main.py, reemplazar:
CORS(app)

# Por:
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 📝 CONCLUSIÓN

### Estado Actual
- ✅ Backend: **Funcional y completo**
- ❌ Frontend: **Interfaz bonita pero sin integración**
- ❌ Integración: **0% completada**

### Para que funcione el proyecto completo necesitas:
1. 🔴 **CRÍTICO**: Integrar API en el formulario de búsqueda
2. 🔴 **CRÍTICO**: Agregar campo "sector" al formulario
3. 🔴 **CRÍTICO**: Conectar dashboard con datos reales del backend
4. 🟡 **IMPORTANTE**: Implementar manejo de errores y estados de carga
5. 🟢 **OPCIONAL**: Mejorar UX y validaciones

### Tiempo Estimado de Integración
- **Mínimo viable**: 3-4 horas
- **Completo con UX**: 8-10 horas

---

**Última actualización**: 2025-11-29
