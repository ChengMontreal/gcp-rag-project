# src/chatbot/lib/chain.py

from google.cloud import storage, aiplatform
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import vertexai
from vertexai.language_models import TextEmbeddingModel

# CORRECTED IMPORT: Absolute path from the project root
from chatbot.config import (
    PROJECT_ID,
    REGION,
    BUCKET_NAME,
    ME_INDEX_ENDPOINT_ID,
    ME_INDEX_ID,
)

# --- Initialize Global Clients (cached by Streamlit) ---
# NOTE: This section might cause an error if env vars are not set when the app starts.
# A more robust app would initialize these inside a function.
vertexai.init(project=PROJECT_ID, location=REGION)
gcs_client = storage.Client(project=PROJECT_ID)
gcs_bucket = gcs_client.bucket(BUCKET_NAME)
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
llm = ChatVertexAI(model_name="gemini-2.5-flash", location=REGION)
vector_search_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=ME_INDEX_ENDPOINT_ID)

# --- Custom Retrieval Function ---
def retrieve_context(query: str) -> str:
    """
    1. Finds similar vectors in Vector Search.
    2. Retrieves the corresponding text chunks from GCS.
    3. Joins them to create context.
    """
    print(f"Retrieving context for query: {query}")
    query_embedding = embedding_model.get_embeddings([query])[0].values
    
    # This is the ID from when you deployed the stream-update index
    deployed_index_id = "rag_index_stream_v1"
    
    neighbors = vector_search_endpoint.find_neighbors(
        queries=[query_embedding],
        deployed_index_id=deployed_index_id,
        num_neighbors=5
    )

    context_chunks = []
    neighbor_ids = [neighbor.id for neighbor in neighbors[0]]
    print(f"Found neighbor IDs: {neighbor_ids}")
    
    for datapoint_id in neighbor_ids:
        try:
            blob = gcs_bucket.blob(f"text_chunks/{datapoint_id}.txt")
            chunk_text = blob.download_as_text()
            context_chunks.append(chunk_text)
        except Exception as e:
            print(f"Warning: Could not retrieve chunk for ID {datapoint_id}: {e}")
            
    if not context_chunks:
        return "No relevant context found."
        
    return "\n---\n".join(context_chunks)


# --- LangChain Expression Language (LCEL) Chains ---
rag_template = """
Use the following pieces of context to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
rag_prompt = PromptTemplate.from_template(rag_template)

rag_chain = (
    {"context": retrieve_context, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

def get_chain():
    """Returns the fully constructed RAG chain."""
    return rag_chain