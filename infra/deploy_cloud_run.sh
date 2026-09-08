#!/usr/bin/env bash
# ==============================================================================
# StudioSonar - Google Cloud Run Deployment Script
# ==============================================================================

set -euo pipefail

# Configuration Defaults (Can be overridden by env vars)
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_LOCATION:-us-central1}"
SERVICE_NAME="studiosonar-taskmaster"
DATASET_NAME="${BIGQUERY_DATASET:-studiosonar_analytics}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"
# Read keys from environment or .env
GEMINI_KEY="${GEMINI_API_KEY:-your_gemini_api_key_here}"
YOUTUBE_KEY="${YOUTUBE_DATA_API_KEY:-your_youtube_api_key_here}"

echo "================================================================="
echo "🚀 Deploying StudioSonar Taskmaster to Google Cloud Platform"
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Service:  ${SERVICE_NAME}"
echo "Dataset:  ${DATASET_NAME}"
echo "================================================================="

if [ -z "${PROJECT_ID}" ]; then
  echo "❌ ERROR: No GCP Project ID found. Please set GCP_PROJECT_ID or run 'gcloud config set project <ID>'."
  exit 1
fi

# Step 1: Enable required GCP Services
echo "📦 Step 1: Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  youtube.googleapis.com \
  --project="${PROJECT_ID}"

# Step 1.5: Configure Dedicated Zero-Secret Service Account
echo "🛡️ Step 1.5: Configuring Dedicated IAM Service Account with Vertex AI Grounding..."
SA_NAME="studio-sonar-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Studio Sonar Autonomous Multi-Agent Service Account" \
  --project="${PROJECT_ID}" 2>/dev/null || echo "Service account ${SA_NAME} already exists."

echo "Binding IAM Roles (Vertex AI Search Grounding, BigQuery, PubSub)..."
for ROLE in \
  "roles/aiplatform.user" \
  "roles/bigquery.dataEditor" \
  "roles/bigquery.jobUser" \
  "roles/pubsub.publisher" \
  "roles/secretmanager.secretAccessor"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None >/dev/null 2>&1 || true
done

# Step 2: Initialize BigQuery Schema
echo "📊 Step 2: Initializing BigQuery Dataset and Tables..."
bq show --project_id="${PROJECT_ID}" "${DATASET_NAME}" >/dev/null 2>&1 || \
  bq mk --project_id="${PROJECT_ID}" --location="${REGION}" --dataset "${DATASET_NAME}"

# Execute SQL DDL
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" < infra/bq_schema.sql || true

# Step 3: Build Container Image via Google Cloud Build
echo "🏗️ Step 3: Building Container Image with Cloud Build..."
gcloud builds submit --tag "${IMAGE_NAME}" --project="${PROJECT_ID}" .

# Step 4: Deploy using Official Google ADK CLI Engine (Agent-to-Agent, Cloud Trace & OTel)
echo "🚀 Step 4: Deploying with Official Google ADK CLI Engine..."
adk deploy cloud_run \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service_name="${SERVICE_NAME}" \
  --a2a \
  --trace_to_cloud \
  --otel_to_cloud \
  src/agents \
  -- \
  --service-account="${SA_EMAIL}" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},EXECUTION_MODE=live,GEMINI_API_KEY=${GEMINI_KEY},GEMINI_MODEL=gemini-3.8-flash,YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY},USE_VERTEX_SEARCH_GROUNDING=true,GOOGLE_SEARCH_ENABLED=true,CLICKHOUSE_HOST=sfzvgvl2p7.us-central1.gcp.clickhouse.cloud,CLICKHOUSE_PORT=8443,CLICKHOUSE_USER=default,CLICKHOUSE_PASSWORD=ZoUQbd24Iv~~J,CLICKHOUSE_DATABASE=default,CLICKHOUSE_SECURE=true,TRIGGER_ACTIVE_WINDOW_ENABLED=true,TRIGGER_START_HOUR=8,TRIGGER_END_HOUR=18,TRIGGER_TIMEZONE=Asia/Ho_Chi_Minh" || \
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_NAME}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --cpu-throttling \
  --timeout=60s \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},EXECUTION_MODE=live,GEMINI_API_KEY=${GEMINI_KEY},GEMINI_MODEL=gemini-3.8-flash,YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY},USE_VERTEX_SEARCH_GROUNDING=true,GOOGLE_SEARCH_ENABLED=true,CLICKHOUSE_HOST=sfzvgvl2p7.us-central1.gcp.clickhouse.cloud,CLICKHOUSE_PORT=8443,CLICKHOUSE_USER=default,CLICKHOUSE_PASSWORD=ZoUQbd24Iv~~J,CLICKHOUSE_DATABASE=default,CLICKHOUSE_SECURE=true,TRIGGER_ACTIVE_WINDOW_ENABLED=true,TRIGGER_START_HOUR=8,TRIGGER_END_HOUR=18,TRIGGER_TIMEZONE=Asia/Ho_Chi_Minh"

# Step 5: Deploy Google Cloud Run Job (Autonomous Google ADK Multi-Agent Runner)
echo "🤖 Step 5: Deploying Google Cloud Run Job (ADK Multi-Agent Runner)..."
gcloud run jobs create "${SERVICE_NAME}-job" \
  --image="${IMAGE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --command="python3" \
  --args="-m,src.demo.run_taskmaster_demo" \
  --memory=512Mi \
  --cpu=1 \
  --max-retries=1 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},EXECUTION_MODE=live,GEMINI_API_KEY=${GEMINI_KEY},GEMINI_MODEL=gemini-3.8-flash,YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY},USE_VERTEX_SEARCH_GROUNDING=true,GOOGLE_SEARCH_ENABLED=true" || \
gcloud run jobs update "${SERVICE_NAME}-job" \
  --image="${IMAGE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SA_EMAIL}" \
  --command="python3" \
  --args="-m,src.demo.run_taskmaster_demo" \
  --memory=512Mi \
  --cpu=1 \
  --max-retries=1 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},EXECUTION_MODE=live,GEMINI_API_KEY=${GEMINI_KEY},GEMINI_MODEL=gemini-3.8-flash,YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY},USE_VERTEX_SEARCH_GROUNDING=true,GOOGLE_SEARCH_ENABLED=true"


# Step 6: Create Google Cloud Pub/Sub Agent Event Bus
echo "📨 Step 6: Initializing Google Cloud Pub/Sub Topic..."
gcloud pubsub topics create studiosonar-agent-events --project="${PROJECT_ID}" || true

# Step 7: Create Cloud Scheduler Autonomous Heartbeat Job (Every 1 Hour)
echo "⏱️ Step 7: Configuring Cloud Scheduler Autonomous Heartbeat (1-Hour Interval)..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format="value(status.url)")

gcloud scheduler jobs create http "${SERVICE_NAME}-heartbeat" \
  --location="${REGION}" \
  --schedule="0 * * * *" \
  --uri="${SERVICE_URL}/api/v1/trigger-cycle" \
  --http-method=POST \
  --project="${PROJECT_ID}" \
  --description="Autonomous 1-hour heartbeat triggering Google ADK Multi-Agent Taskmaster cycle" || \
gcloud scheduler jobs update http "${SERVICE_NAME}-heartbeat" \
  --location="${REGION}" \
  --schedule="0 * * * *" \
  --uri="${SERVICE_URL}/api/v1/trigger-cycle" \
  --http-method=POST \
  --project="${PROJECT_ID}" \
  --description="Autonomous 1-hour heartbeat triggering Google ADK Multi-Agent Taskmaster cycle"

echo "================================================================="
echo "✅ SUCCESS: Full Google ADK Architecture is Live on Google Cloud!"
echo "Web Command Center: ${SERVICE_URL}"
echo "Cloud Run Job:      ${SERVICE_NAME}-job"
echo "Cloud Scheduler:    ${SERVICE_NAME}-heartbeat (Every 1h)"
echo "Pub/Sub Event Bus:  projects/${PROJECT_ID}/topics/studiosonar-agent-events"
echo "Health Check:       ${SERVICE_URL}/healthz"
echo "================================================================="


