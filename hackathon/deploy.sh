#!/bin/bash

set -e

PROJECT_ID=${GCP_PROJECT_ID:-}
REGION=${GCP_REGION:-us-central1}
JOB_NAME=${CLOUD_RUN_JOB_NAME:-instagram-search}
APIFY_TOKEN=${APIFY_API_TOKEN:-}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID not set"
    exit 1
fi

if [ -z "$APIFY_TOKEN" ]; then
    echo "Error: APIFY_API_TOKEN not set"
    exit 1
fi

echo "Deploying Cloud Run Job: ${JOB_NAME}"
echo "This will build the image automatically using Cloud Build (no Docker required locally)"

gcloud run jobs deploy "${JOB_NAME}" \
    --source . \
    --region "${REGION}" \
    --set-env-vars "APIFY_API_TOKEN=${APIFY_TOKEN}" \
    --max-retries 1 \
    --task-timeout 3600 \
    --cpu 2 \
    --memory 4Gi \
    --project "${PROJECT_ID}"

echo ""
echo "✅ Deployment successful!"
echo "Job name: ${JOB_NAME}"
echo "Region: ${REGION}"
echo ""
echo "To execute the job, run:"
echo "gcloud run jobs execute ${JOB_NAME} --region ${REGION} --project ${PROJECT_ID}"

