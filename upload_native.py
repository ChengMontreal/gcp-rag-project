import os
import sys
import argparse
import uuid
import glob
from typing import List

# --- DEPENDENCIES ---
from pypdf import PdfReader
from google.cloud import aiplatform, storage
import vertexai
from vertexai.language_models import TextEmbeddingModel

# --- Simple Text Splitter ---
def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    if not text: return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

# --- CONFIGURATION ---
try:
    PROJECT_ID = os.environ["PROJECT_ID"]
    REGION = os.environ["REGION"]
    BUCKET_NAME = os.environ["BUCKET_NAME"]
    ME_INDEX_ID = os.environ["ME_INDEX_ID_VALUE"]
except KeyError as e:
    print(f"❌ ERROR: Environment variable {e} is not set. Please run 'source setup_env.sh' first.")
    sys.exit(1)

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload all PDFs from a directory to Vertex AI Vector Search using Stream Update.")
    parser.add_argument("directory", nargs="?", default="./data", help="Path to the directory containing PDF files. Defaults to './data'.")
    args = parser.parse_args()

    # 1. Initialize Clients
    try:
        print("--- Initializing Google Cloud Clients ---")
        vertexai.init(project=PROJECT_ID, location=REGION)
        embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        vector_search_index = aiplatform.MatchingEngineIndex(index_name=ME_INDEX_ID)
        gcs_client = storage.Client(project=PROJECT_ID)
        gcs_bucket = gcs_client.bucket(BUCKET_NAME)
        print("✅ Clients initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize clients: {e}")
        sys.exit(1)

    # 2. Find and Process Files
    pdf_directory = args.directory
    if not os.path.isdir(pdf_directory):
        print(f"❌ ERROR: Directory '{pdf_directory}' not found.")
        sys.exit(1)

    pdf_files = glob.glob(os.path.join(pdf_directory, "*.[pP][dD][fF]"))
    if not pdf_files:
        print(f"🤷 No PDF files found in '{pdf_directory}'.")
        sys.exit(0)

    print(f"\n✨ Found {len(pdf_files)} PDF(s). Starting real-time upload...")
    
    gcs_chunk_folder = "text_chunks"

    # 3. Process each PDF file and upload its chunks in real-time
    for pdf_path in pdf_files:
        try:
            print(f"▶️ Processing: {os.path.basename(pdf_path)}")
            reader = PdfReader(pdf_path)
            full_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
            if not full_text.strip():
                print(f"  - 🤷 Warning: No text extracted. Skipping file.")
                continue
            
            chunks = split_text_into_chunks(full_text)
            if not chunks: continue
            
            embeddings = embedding_model.get_embeddings(chunks)
            
            datapoints_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding.values and isinstance(embedding.values, list) and len(embedding.values) > 0:
                    datapoint_id = str(uuid.uuid4())
                    
                    # Save the text chunk to GCS for retrieval by the app
                    chunk_blob = gcs_bucket.blob(f"{gcs_chunk_folder}/{datapoint_id}.txt")
                    chunk_blob.upload_from_string(chunk, content_type="text/plain")
                    
                    # Prepare the vector for the real-time upsert
                    datapoint = {
                        "datapoint_id": datapoint_id,
                        "feature_vector": embedding.values
                    }
                    datapoints_to_upsert.append(datapoint)

            # Upload the vectors for this document
            if datapoints_to_upsert:
                print(f"  - ☁️ Uploading {len(datapoints_to_upsert)} vectors for this document...")
                vector_search_index.upsert_datapoints(datapoints=datapoints_to_upsert)
                print(f"  - ✅ Success.")
        except Exception as e:
            print(f"  - ❌ Error processing file {os.path.basename(pdf_path)}: {e}")

    print("\n🎉 Mission Accomplished! All files have been processed and uploaded.")