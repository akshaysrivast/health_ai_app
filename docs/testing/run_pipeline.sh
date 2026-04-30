#!/usr/bin/env sh
set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
PAYLOAD_FILE="${PAYLOAD_FILE:-docs/testing/sample_patient_metabolic.json}"

echo "Submitting patient payload to ${BACKEND_URL}/analyze"
curl --silent --show-error --location "${BACKEND_URL}/analyze" \
  --header "Content-Type: application/json" \
  --data "@${PAYLOAD_FILE}" | tee docs/testing/last_pipeline_response.json

echo
echo "Saved response to docs/testing/last_pipeline_response.json"
