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

# Create or Update Autonomous Cycle Scheduler Job (15 min)
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

echo "✅ SUCCESS: Cloud Scheduler job '${JOB_NAME}' active (every 15 min)."

# ==============================================================================
# U1: ClickHouse High-Frequency Radar Loop (1-minute schedule)
# ==============================================================================
RADAR_JOB_NAME="studiosonar-radar-tick-cron"
RADAR_SCHEDULE="* * * * *" # Every 1 minute
RADAR_URI="${SERVICE_URL}/api/v1/radar-tick"

echo "⏰ Setting up Cloud Scheduler for High-Frequency Radar Tick (* * * * *)"
gcloud scheduler jobs create http "${RADAR_JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${RADAR_SCHEDULE}" \
  --uri="${RADAR_URI}" \
  --http-method=POST \
  --description="Every 1-min ClickHouse hot radar scan for instant velocity spikes & brigade detection" \
  --time-zone="UTC" \
  --project="${PROJECT_ID}" || \
gcloud scheduler jobs update http "${RADAR_JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${RADAR_SCHEDULE}" \
  --uri="${RADAR_URI}" \
  --http-method=POST \
  --description="Every 1-min ClickHouse hot radar scan for instant velocity spikes & brigade detection" \
  --time-zone="UTC" \
  --project="${PROJECT_ID}"

echo "✅ SUCCESS: Cloud Scheduler job '${RADAR_JOB_NAME}' active (every 1 min)."

