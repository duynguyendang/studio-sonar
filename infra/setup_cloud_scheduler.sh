#!/usr/bin/env bash
# ==============================================================================
# StudioSonar - Google Cloud Scheduler Cron Trigger Setup
# Configures 24/7 background Taskmaster execution on Cloud Run
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_LOCATION:-us-central1}"
SERVICE_NAME="studiosonar-taskmaster"
JOB_NAME="studiosonar-cycle-cron"
SCHEDULE="*/15 * * * *" # Every 15 minutes

if [ -z "${PROJECT_ID}" ]; then
  echo "❌ ERROR: No GCP Project ID found."
  exit 1
fi

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format="value(status.url)")
TARGET_URI="${SERVICE_URL}/api/v1/trigger-cycle"

echo "================================================================="
echo "⏰ Setting up Cloud Scheduler for StudioSonar Taskmaster"
echo "Schedule: ${SCHEDULE} (Every 15 minutes)"
echo "Target:   ${TARGET_URI}"
echo "================================================================="

# Create or Update Scheduler Job
gcloud scheduler jobs create http "${JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${SCHEDULE}" \
  --uri="${TARGET_URI}" \
  --http-method=POST \
  --description="24/7 Autonomous trigger for StudioSonar Taskmaster Agent" \
  --time-zone="UTC" \
  --project="${PROJECT_ID}" || \
gcloud scheduler jobs update http "${JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${SCHEDULE}" \
  --uri="${TARGET_URI}" \
  --http-method=POST \
  --description="24/7 Autonomous trigger for StudioSonar Taskmaster Agent" \
  --time-zone="UTC" \
  --project="${PROJECT_ID}"

echo "✅ SUCCESS: Cloud Scheduler job '${JOB_NAME}' active and triggering StudioSonar every 15 minutes."
