# 🔄 Flujo de Datos: Estado Actual vs Esperado

## 📊 DIAGRAMA DE ARQUITECTURA

### ❌ ESTADO ACTUAL (NO FUNCIONA)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     (Next.js - Puerto 3000)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SplashScreen (/)                                        │
│     └─> Pantalla inicial                                    │
│                                                              │
│  2. SearchScreen (/buscar)                                  │
│     ├─> Formulario con:                                     │
│     │   ✅ Company Name                                     │
│     │   ✅ Country (Peru/Chile)                            │
│     │   ❌ Sector (FALTA)                                  │
│     │   ✅ Keywords                                         │
│     │                                                        │
│     └─> handleSubmit()                                      │
│         └─> ❌ NO HACE NADA                                │
│             └─> Solo redirige a /dashboard                  │
│                 SIN ENVIAR DATOS                             │
│                                                              │
│  3. DashboardScreen (/dashboard)                            │
│     └─> ❌ Muestra datos HARDCODEADOS                      │
│         ├─> Empresa: "Rappi" (fijo)                        │
│         ├─> Menciones: 32k (fijo)                          │
│         ├─> Aprobación: 89% (fijo)                         │
│         └─> 30 menciones sociales (datos de ejemplo)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                    ❌ NO HAY COMUNICACIÓN ❌

┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                     (Flask - Puerto 5000)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  API Endpoints:                                             │
│  ├─> GET  /          ✅ Health check                       │
│  ├─> POST /search    ✅ Búsqueda con IA                    │
│  └─> GET  /results   ✅ Obtener resultados                 │
│                                                              │
│  Funcionalidades:                                           │
│  ├─> ✅ Análisis de keywords con DeepSeek AI              │
│  ├─> ✅ Detección de sinónimos                            │
│  ├─> ✅ Base de datos MySQL                               │
│  ├─> ✅ Caché de componentes                              │
│  └─> ✅ Generación de análisis final                      │
│                                                              │
│  ⚠️ PROBLEMA: Nadie lo está usando                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ ESTADO ESPERADO (CÓMO DEBERÍA FUNCIONAR)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     (Next.js - Puerto 3000)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SplashScreen (/)                                        │
│     └─> Pantalla inicial                                    │
│         └─> Click "Start" → /buscar                         │
│                                                              │
│  2. SearchScreen (/buscar)                                  │
│     ├─> Formulario con:                                     │
│     │   ✅ Company Name                                     │
│     │   ✅ Country (Peru/Chile)                            │
│     │   ✅ Sector (Technology, Food, etc.) ← AGREGAR       │
│     │   ✅ Keywords                                         │
│     │                                                        │
│     └─> handleSubmit()                                      │
│         ├─> ✅ Validar campos                              │
│         ├─> ✅ setIsSubmitting(true)                       │
│         ├─> ✅ Llamar API Backend                          │
│         │   │                                               │
│         │   └──────────────────────┐                        │
│         │                          │                        │
│         │   ┌──────────────────────▼──────────┐            │
│         │   │   POST /search                  │            │
│         │   │   {                             │            │
│         │   │     name: "Rappi",              │            │
│         │   │     country: "peru",            │            │
│         │   │     sector: "Technology",       │            │
│         │   │     keyword: "delivery app"     │            │
│         │   │   }                             │            │
│         │   └──────────────────────┬──────────┘            │
│         │                          │                        │
│         ├─> ✅ Recibir respuesta  │                        │
│         ├─> ✅ Guardar en Context/LocalStorage              │
│         └─> ✅ Redirigir a /dashboard                      │
│                                                              │
│  3. DashboardScreen (/dashboard)                            │
│     ├─> ✅ Cargar datos del Context/LocalStorage           │
│     ├─> ✅ Mostrar datos REALES:                           │
│     │   ├─> Nombre de empresa (del backend)                │
│     │   ├─> País y sector (del backend)                    │
│     │   ├─> Análisis de keywords (del backend)             │
│     │   ├─> Summary y findings (del backend)               │
│     │   ├─> Recommendations (del backend)                  │
│     │   └─> Overall score (del backend)                    │
│     │                                                        │
│     └─> ✅ Botón "Generate Report"                         │
│         └─> Exportar análisis completo                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ✅ COMUNICACIÓN HTTP ✅
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                     (Flask - Puerto 5000)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Recibe POST /search                                     │
│     └─> Valida campos requeridos                            │
│                                                              │
│  2. Procesa Keywords con IA                                 │
│     ├─> analyze_keywords_with_ai()                          │
│     │   └─> DeepSeek AI optimiza keywords                   │
│     │                                                        │
│     ├─> Para cada keyword:                                  │
│     │   ├─> Busca en BD (get_component_from_db)            │
│     │   ├─> Si no existe:                                   │
│     │   │   ├─> Verifica sinónimos (check_synonym_with_ai) │
│     │   │   └─> Si no hay sinónimo:                        │
│     │   │       └─> Nueva búsqueda (search_with_ai)        │
│     │   │           └─> Guarda en BD                        │
│     │   └─> Retorna resultado                               │
│     │                                                        │
│     └─> generate_final_results_with_ai()                    │
│         └─> Consolida análisis completo                     │
│                                                              │
│  3. Guarda en Historial                                     │
│     └─> save_search_history()                               │
│         └─> MySQL: tabla search_history                     │
│                                                              │
│  4. Retorna JSON                                            │
│     └─> {                                                    │
│           company_name,                                      │
│           country,                                           │
│           sector,                                            │
│           keyword_analysis: [...],                          │
│           final_analysis: {                                 │
│             summary,                                         │
│             key_findings,                                    │
│             recommendations,                                 │
│             overall_score                                    │
│           }                                                  │
│         }                                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BASE DE DATOS                           │
│                      (MySQL - Puerto 3306)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tablas:                                                     │
│  ├─> components                                             │
│  │   └─> Caché de keywords y análisis                       │
│  │                                                           │
│  └─> search_history                                         │
│      └─> Historial de búsquedas realizadas                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 FLUJO DETALLADO DE UNA BÚSQUEDA

### Paso 1: Usuario llena formulario
```
Usuario en /buscar
├─> Ingresa: "Rappi"
├─> Selecciona: "Peru"
├─> Selecciona: "Technology" ← FALTA AGREGAR
└─> Escribe: "delivery app innovation"
```

### Paso 2: Frontend envía request
```javascript
// ❌ ACTUAL (no hace nada)
router.push("/dashboard")

// ✅ ESPERADO
const response = await fetch('http://localhost:5000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Rappi",
    country: "peru",
    sector: "Technology",
    keyword: "delivery app innovation"
  })
})
```

### Paso 3: Backend procesa
```python
# 1. Valida campos
required_fields = ['name', 'country', 'sector', 'keyword']

# 2. Analiza keywords con IA
optimized_keywords = analyze_keywords_with_ai("delivery app innovation")
# Resultado: ["delivery", "app", "innovation"]

# 3. Para cada keyword:
for keyword in optimized_keywords:
    # Busca en BD
    db_result = get_component_from_db(keyword)
    
    if not db_result:
        # Verifica sinónimos
        synonym = check_synonym_with_ai(keyword, existing_keywords)
        
        if not synonym:
            # Nueva búsqueda con IA
            result = search_with_ai(keyword, "Technology", "peru")
            # Guarda en BD
            save_component_to_db(keyword, result)

# 4. Genera análisis final
final_analysis = generate_final_results_with_ai(
    keyword_results,
    "Rappi",
    "Technology",
    "peru"
)

# 5. Retorna JSON completo
return {
    "company_name": "Rappi",
    "country": "peru",
    "sector": "Technology",
    "keyword_analysis": [...],
    "final_analysis": {
        "summary": "Rappi es una empresa líder...",
        "key_findings": ["Alto crecimiento", "Innovación"],
        "recommendations": ["Expandir mercado", "Mejorar app"],
        "overall_score": 85
    }
}
```

### Paso 4: Frontend recibe y muestra
```javascript
// ✅ ESPERADO
const data = await response.json()

// Guardar para dashboard
localStorage.setItem('searchResult', JSON.stringify(data))

// Redirigir
router.push('/dashboard')

// En dashboard:
const result = JSON.parse(localStorage.getItem('searchResult'))

// Mostrar:
// - Nombre: result.company_name
// - Análisis: result.final_analysis.summary
// - Score: result.final_analysis.overall_score
// - Findings: result.final_analysis.key_findings
// - Recommendations: result.final_analysis.recommendations
```

---

## 🎯 RESUMEN DE CAMBIOS NECESARIOS

### En Frontend:

1. **search-screen.tsx**
   - ✅ Agregar campo `sector`
   - ✅ Implementar llamada API en `handleSubmit`
   - ✅ Agregar manejo de errores
   - ✅ Agregar loading state

2. **dashboard-screen.tsx**
   - ✅ Recibir datos del backend
   - ✅ Reemplazar datos hardcodeados
   - ✅ Mapear estructura de datos

3. **Nuevo: lib/api.ts**
   - ✅ Crear servicio para llamadas API
   - ✅ Definir interfaces TypeScript

4. **Nuevo: Context o State Management**
   - ✅ Compartir datos entre páginas
   - ✅ Evitar prop drilling

### En Backend:

✅ **NO REQUIERE CAMBIOS** - El backend está completo y funcional

Solo necesitas:
- ✅ Configurar `.env` con DEEPSEEK_API_KEY
- ✅ Configurar MySQL y ejecutar `setup_database.sql`
- ✅ Actualizar contraseña en `main.py`

---

## 📊 CHECKLIST DE INTEGRACIÓN

### Preparación
- [ ] Backend: Configurar `.env`
- [ ] Backend: Configurar MySQL
- [ ] Backend: Ejecutar `setup_database.sql`
- [ ] Backend: Iniciar servidor (`python main.py`)

### Desarrollo Frontend
- [ ] Crear `lib/api.ts` con servicio API
- [ ] Agregar campo "sector" al formulario
- [ ] Implementar llamada API en `handleSubmit`
- [ ] Crear Context para compartir datos
- [ ] Actualizar Dashboard para usar datos reales
- [ ] Agregar manejo de errores
- [ ] Agregar loading states

### Testing
- [ ] Probar formulario completo
- [ ] Verificar llamada al backend
- [ ] Verificar datos en dashboard
- [ ] Probar manejo de errores
- [ ] Verificar guardado en BD

### Producción
- [ ] Configurar variables de entorno
- [ ] Configurar CORS correctamente
- [ ] Optimizar llamadas API
- [ ] Agregar validaciones adicionales

---

**Creado**: 2025-11-29  
**Proyecto**: ProyectHack - UNHEVAL Hackathon
