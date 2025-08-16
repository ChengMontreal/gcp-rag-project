import os
import sys
import json
from google.cloud import aiplatform

# --- CONFIGURATION ---
try:
    PROJECT_ID = os.environ["PROJECT_ID"]
    REGION = os.environ["REGION"]
    ME_INDEX_ID = os.environ["ME_INDEX_ID_VALUE"]
    JSON_FILE_PATH = "datapoints_batch_upload.json"
except KeyError as e:
    print(f"❌ ERROR: Environment variable {e} is not set.")
    print("Please make sure you have created and sourced your 'setup_env.sh' file.")
    sys.exit(1)

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    print("--- Starting Index Cleanup Script ---")

    # 1. Initialize the AI Platform client for the specific index
    try:
        aiplatform.init(project=PROJECT_ID, location=REGION)
        vector_search_index = aiplatform.MatchingEngineIndex(index_name=ME_INDEX_ID)
        print(f"✅ Initialized connection to index '{ME_INDEX_ID}'.")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        sys.exit(1)

    # 2. Read all datapoint IDs from our local JSON file
    if not os.path.exists(JSON_FILE_PATH):
        print(f"🤷 File '{JSON_FILE_PATH}' not found. No IDs to delete.")
        sys.exit(0)

    print(f"📖 Reading vector IDs from '{JSON_FILE_PATH}'...")
    ids_to_delete = []
    with open(JSON_FILE_PATH, "r") as f:
        for line in f:
            try:
                # The batch file format uses the 'id' key
                data = json.loads(line)
                if "id" in data:
                    ids_to_delete.append(data["id"])
            except json.JSONDecodeError:
                continue # Ignore empty or malformed lines

    if not ids_to_delete:
        print(f"🤷 No valid IDs found in the file to delete.")
        sys.exit(0)

    print(f"✨ Found {len(ids_to_delete)} vector IDs to delete.")

    # 3. Call the correct remove_datapoints method
    print(f"🚀 Sending request to delete {len(ids_to_delete)} datapoints from the index...")
    try:
        # CORRECTED METHOD NAME: remove_datapoints
        vector_search_index.remove_datapoints(datapoint_ids=ids_to_delete)
        print("\n🎉 Success! Deletion request was sent.")
        print("   It may take a few moments for the 'Dense count' in the GCP Console to update to 0.")
    except Exception as e:
        print(f"❌ An error occurred during deletion: {e}")