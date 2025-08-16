# src/chatbot/config.py

import os

# --- CORE GCP CONFIGURATION ---
# These will be loaded from the environment variables set by Cloud Run
# or our local setup_env.sh script.
PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")

# --- VECTOR SEARCH CONFIGURATION ---
ME_INDEX_ID = os.environ.get("ME_INDEX_ID_VALUE")
ME_INDEX_ENDPOINT_ID = os.environ.get("ME_INDEX_ENDPOINT_ID_VALUE")
BUCKET_NAME = os.environ.get("BUCKET_NAME")