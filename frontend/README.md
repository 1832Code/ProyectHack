# 🚀 Entropy Frontend - Sistema de Búsqueda Empresarial

Frontend de la aplicación Entropy desarrollado con Next.js para el Hackathon UNHEVAL.

## 🌐 Despliegue

**URL de Producción:** https://proyecthacks.onrender.com

## 🛠️ Tecnologías

- **Next.js** 16.0.3 - Framework React
- **NextAuth.js** - Autenticación con Google OAuth
- **Tailwind CSS** - Estilos
- **TypeScript** - Tipado estático
- **Supabase** - Base de datos

## 🚀 Instalación Local

1. **Clonar el repositorio**
```bash
git clone <tu-repo>
cd frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
- Google OAuth (Client ID y Secret)
- Supabase (URL y Keys)
- NextAuth Secret

4. **Ejecutar en desarrollo**
```bash
npm run dev
```

## 📦 Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build de producción
- `npm start` - Servidor de producción
- `npm run lint` - Linter

## 🔧 Configuración para Despliegue

### Variables de Entorno Requeridas

```env
NEXTAUTH_URL=https://proyecthacks.onrender.com
NEXTAUTH_SECRET=tu-secret-seguro
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
SUPABASE_ANON_KEY=tu-anon-key
```

### Render.com

1. Conecta tu repositorio de GitHub
2. Configura las variables de entorno
3. Build Command: `npm run build`
4. Start Command: `npm start`

## 🔐 Seguridad

- Variables sensibles excluidas del repositorio
- Headers de seguridad configurados
- Autenticación OAuth segura
- Validación de dominios para imágenes

## 📁 Estructura

```
frontend/
├── app/                 # App Router de Next.js
├── components/          # Componentes React
├── lib/                # Utilidades y configuración
├── public/             # Archivos estáticos
├── .env.example        # Ejemplo de variables de entorno
└── next.config.mjs     # Configuración de Next.js
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Proyecto educativo para Hackathon UNHEVAL.