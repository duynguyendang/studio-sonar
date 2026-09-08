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
# FinOps Schedule: Runs only during business/demo hours (09:00 - 18:00 Asia/Ho_Chi_Minh, Mon-Fri)
# Outside this window, scheduler is completely silent, allowing ClickHouse Cloud to Auto-Suspend ($0 compute)
SCHEDULE="0 9,11,13,15,17 * * 1-5" 
TIME_ZONE="Asia/Ho_Chi_Minh"

if [ -z "${PROJECT_ID}" ]; then
  echo "❌ ERROR: No GCP Project ID found."
  exit 1
fi

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform=managed --region="${REGION}" --project="${PROJECT_ID}" --format="value(status.url)")
TARGET_URI="${SERVICE_URL}/api/v1/trigger-cycle"

echo "================================================================="
echo "⏰ Setting up FinOps Cloud Scheduler for StudioSonar Taskmaster"
echo "Schedule:  ${SCHEDULE} (Active window 09:00 - 18:00 Mon-Fri)"
echo "Time Zone: ${TIME_ZONE}"
echo "Target:    ${TARGET_URI}"
echo "Notice:    Allows ClickHouse Cloud to auto-suspend when idle ($0 cost)"
echo "================================================================="

# Create or Update Autonomous Cycle Scheduler Job (FinOps Window)
gcloud scheduler jobs create http "${JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${SCHEDULE}" \
  --uri="${TARGET_URI}" \
  --http-method=POST \
  --description="FinOps Active Window Trigger for StudioSonar Taskmaster Agent (Auto-suspends off-hours)" \
  --time-zone="${TIME_ZONE}" \
  --project="${PROJECT_ID}" || \
gcloud scheduler jobs update http "${JOB_NAME}" \
  --location="${REGION}" \
  --schedule="${SCHEDULE}" \
  --uri="${TARGET_URI}" \
  --http-method=POST \
  --description="FinOps Active Window Trigger for StudioSonar Taskmaster Agent (Auto-suspends off-hours)" \
  --time-zone="${TIME_ZONE}" \
  --project="${PROJECT_ID}"

echo "✅ SUCCESS: Cloud Scheduler job '${JOB_NAME}' configured with FinOps Active Window."

