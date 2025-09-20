from langchain_community.embeddings import OllamaEmbeddings
import os

def InitialzeEmbeddingClient(model_name: str, model_url: str, api_key: str, method: str):
    embeddings = None

    if method == 'ollama':
        embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=model_url
        )
    elif method == 'none' or method == '':
        embeddings = None
    else:
        raise ValueError(f"Unsupported embedding method: {method}")

    return embeddings
