#!/usr/bin/env bash
set -e

# ==============================================================================
# Google Cloud Platform - Distributed Google ADK Multi-Agent Architecture
# Deploys 4 Specialized Agent Microservices + 1 Root Orchestrator on Cloud Run
# ==============================================================================

PROJECT_ID="studiosonar-dev"
REGION="us-central1"
DATASET_NAME="studiosonar_analytics"
IMAGE_NAME="gcr.io/${PROJECT_ID}/studiosonar-taskmaster:latest"
YOUTUBE_KEY="${YOUTUBE_DATA_API_KEY:-AIzaSyAV5KupWHw65Y-EMtuEcgm7DFkszYyBOx4}"

echo "================================================================="
echo "🚀 Deploying Distributed Google ADK Multi-Agent Architecture"
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Model:    gemini-3.7-flash (Vertex AI Zero-Key)"
echo "Image:    ${IMAGE_NAME}"
echo "================================================================="

# Common flags for FinOps protection (Scale to 0 when idle)
COMMON_FLAGS="--image=${IMAGE_NAME} --platform=managed --region=${REGION} --project=${PROJECT_ID} --allow-unauthenticated --min-instances=0 --max-instances=2 --memory=512Mi --cpu=1 --concurrency=80 --cpu-throttling --timeout=60s --quiet"

# Step 1: Deploy Specialized Agent Microservices
echo "🤖 Step 1.1: Deploying ChannelMonitorAgent Service..."
gcloud run deploy studiosonar-channel-monitor ${COMMON_FLAGS} \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},GCS_REPORTS_BUCKET=studiosonar-dev-reports,EXECUTION_MODE=live,GEMINI_MODEL=gemini-3.7-flash,GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY}"

CHANNEL_MONITOR_URL=$(gcloud run services describe studiosonar-channel-monitor --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ ChannelMonitorAgent Live: ${CHANNEL_MONITOR_URL}"

echo "🤖 Step 1.2: Deploying AnomalyDetectorAgent Service..."
gcloud run deploy studiosonar-anomaly-detector ${COMMON_FLAGS} \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},GCS_REPORTS_BUCKET=studiosonar-dev-reports,EXECUTION_MODE=live,GEMINI_MODEL=gemini-3.7-flash,GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY}"

ANOMALY_DETECTOR_URL=$(gcloud run services describe studiosonar-anomaly-detector --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ AnomalyDetectorAgent Live: ${ANOMALY_DETECTOR_URL}"

echo "🤖 Step 1.3: Deploying PRCrisisStrategistAgent Service..."
gcloud run deploy studiosonar-pr-strategist ${COMMON_FLAGS} \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},GCS_REPORTS_BUCKET=studiosonar-dev-reports,EXECUTION_MODE=live,GEMINI_MODEL=gemini-3.7-flash,GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY}"

PR_STRATEGIST_URL=$(gcloud run services describe studiosonar-pr-strategist --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ PRCrisisStrategistAgent Live: ${PR_STRATEGIST_URL}"

echo "🤖 Step 1.4: Deploying ViralContentCreatorAgent Service..."
gcloud run deploy studiosonar-content-creator ${COMMON_FLAGS} \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},GCS_REPORTS_BUCKET=studiosonar-dev-reports,EXECUTION_MODE=live,GEMINI_MODEL=gemini-3.7-flash,GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY}"

CONTENT_CREATOR_URL=$(gcloud run services describe studiosonar-content-creator --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')
echo "✅ ViralContentCreatorAgent Live: ${CONTENT_CREATOR_URL}"

# Step 2: Deploy Root Taskmaster Orchestrator (Connected via A2A Endpoints)
echo "👑 Step 2: Deploying Root Taskmaster Orchestrator with A2A Mesh..."
gcloud run deploy studiosonar-taskmaster \
  --image="${IMAGE_NAME}" \
  --platform=managed \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --cpu-throttling \
  --timeout=60s \
  --quiet \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},BIGQUERY_DATASET=${DATASET_NAME},GCS_REPORTS_BUCKET=studiosonar-dev-reports,EXECUTION_MODE=live,GEMINI_MODEL=gemini-3.7-flash,GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},YOUTUBE_DATA_API_KEY=${YOUTUBE_KEY},CHANNEL_MONITOR_URL=${CHANNEL_MONITOR_URL},ANOMALY_DETECTOR_URL=${ANOMALY_DETECTOR_URL},PR_STRATEGIST_URL=${PR_STRATEGIST_URL},CONTENT_CREATOR_URL=${CONTENT_CREATOR_URL}"

ORCHESTRATOR_URL=$(gcloud run services describe studiosonar-taskmaster --region="${REGION}" --project="${PROJECT_ID}" --format='value(status.url)')

# Step 3: Configure Cloud Scheduler Heartbeat (1-Hour Interval)
echo "⏱️ Step 3: Configuring Cloud Scheduler (1-Hour Interval)..."
gcloud scheduler jobs create http studiosonar-taskmaster-heartbeat \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --schedule="0 * * * *" \
  --uri="${ORCHESTRATOR_URL}/api/v1/trigger-cycle" \
  --http-method=POST \
  --attempt-deadline=180s \
  --description="Autonomous 1-hour heartbeat triggering Google ADK Multi-Agent Taskmaster cycle" || \
gcloud scheduler jobs update http studiosonar-taskmaster-heartbeat \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --schedule="0 * * * *" \
  --uri="${ORCHESTRATOR_URL}/api/v1/trigger-cycle" \
  --http-method=POST \
  --attempt-deadline=180s

echo "================================================================="
echo "🎉 DISTRIBUTED GOOGLE ADK MULTI-AGENT ARCHITECTURE IS LIVE!"
echo "👑 Root Orchestrator:       ${ORCHESTRATOR_URL}"
echo "📡 Channel Sentinel Agent:  ${CHANNEL_MONITOR_URL}"
echo "🔍 Anomaly Detector Agent:  ${ANOMALY_DETECTOR_URL}"
echo "🚨 PR Crisis Agent:         ${PR_STRATEGIST_URL}"
echo "✍️ Content Creator Agent:   ${CONTENT_CREATOR_URL}"
echo "⏱️ Cloud Scheduler:         1-Hour Interval (0 * * * *)"
echo "================================================================="
