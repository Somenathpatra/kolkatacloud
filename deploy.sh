#!/bin/bash
# deploy.sh — KolkataCloud Cloud Run deployment script
# Run this from the folder containing app.py, Dockerfile, requirements.txt

set -e  # stop on first error

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
SERVICE_NAME="kolkatacloud"
REGION="asia-south1"   # Mumbai — closest to Kolkata

echo ""
echo "=== KolkataCloud — Cloud Run Deploy ==="
echo "Project : $PROJECT_ID"
echo "Service : $SERVICE_NAME"
echo "Region  : $REGION"
echo ""

# 1. Check required files exist
echo "--- Checking files ---"
for f in app.py Dockerfile requirements.txt; do
  if [ -f "$f" ]; then
    echo "  OK  $f"
  else
    echo "  MISSING  $f  <-- create this file first"
    exit 1
  fi
done

# 2. Check gcloud is logged in
echo ""
echo "--- Checking gcloud auth ---"
gcloud auth print-identity-token > /dev/null 2>&1 || {
  echo "Not logged in. Running: gcloud auth login"
  gcloud auth login
}
echo "  OK  authenticated"

# 3. Enable required APIs (safe to run even if already enabled)
echo ""
echo "--- Enabling APIs ---"
gcloud services enable run.googleapis.com \
                        cloudbuild.googleapis.com \
                        artifactregistry.googleapis.com \
  --project "$PROJECT_ID" --quiet
echo "  OK  APIs enabled"

# 4. Deploy
echo ""
echo "--- Deploying to Cloud Run ---"
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --port 8080 \
  --project "$PROJECT_ID"

echo ""
echo "=== Deploy complete ==="
gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format "value(status.url)"
