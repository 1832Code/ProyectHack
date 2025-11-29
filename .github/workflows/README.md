# GitHub Actions - Deploy Hackathon

Este workflow despliega automáticamente la aplicación de la carpeta `hackathon` a Google Cloud Run Jobs.

## Configuración de Secrets

Para que el workflow funcione, necesitas configurar los siguientes secrets en tu repositorio de GitHub:

### Secrets Requeridos

1. **GCP_SA_KEY**: Clave JSON del Service Account de Google Cloud
   - Ve a Google Cloud Console → IAM & Admin → Service Accounts
   - Crea o selecciona un service account
   - Genera una clave JSON
   - El service account necesita los siguientes roles:
     - Cloud Run Admin
     - Service Account User
     - Cloud Build Service Account

2. **GCP_PROJECT_ID**: ID del proyecto de Google Cloud
   - Ejemplo: `mi-proyecto-123456`

3. **APIFY_API_TOKEN**: Token de API de Apify
   - Obtén tu token desde tu cuenta de Apify

### Secrets Opcionales

4. **GCP_REGION**: Región de Google Cloud (por defecto: `us-central1`)
   - Ejemplo: `us-east1`, `europe-west1`

5. **CLOUD_RUN_JOB_NAME**: Nombre del Cloud Run Job (por defecto: `instagram-search`)
   - Ejemplo: `mi-job-name`

## Cómo configurar los Secrets

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click en "New repository secret"
4. Agrega cada uno de los secrets mencionados arriba

## Cuándo se ejecuta el workflow

- **Push a main/master**: Se ejecuta el despliegue automático
- **Pull Request**: Solo se valida la configuración (no despliega)
- **Manual**: Puedes ejecutarlo manualmente desde la pestaña Actions

## Estructura del workflow

- **Job `validate`**: Valida que los archivos necesarios existan (Dockerfile, requirements.txt, src/)
- **Job `deploy`**: Despliega la aplicación a Cloud Run Jobs

