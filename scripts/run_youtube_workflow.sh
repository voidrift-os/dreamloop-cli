#!/bin/bash

# Execute the YouTube automation workflow using n8n.
# Requires n8n to be installed and API keys available in the environment.

if ! command -v n8n >/dev/null 2>&1; then
  echo "n8n is not installed or not found in PATH." >&2
  exit 1
fi

WORKFLOW="$(dirname "$0")/../youtube_automation_workflow.json"

n8n execute --file "$WORKFLOW"
