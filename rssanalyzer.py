import langchain
import os
import argparse
import logging
from dotenv import load_dotenv
from tinydb import TinyDB, Query
import pandas as pd
import sys
from os.path import join, dirname
from langchain_community.embeddings import OllamaEmbeddings
import glob
from tqdm import tqdm
import umap
import ast
import numpy as np
import pickle

class range_check(object):
    def __init__(self, low_limit=None, high_limit=None, vtype="integer"):
        self.min = low_limit
        self.max = high_limit
        self.type = vtype

    def __contains__(self, val):
        ret = True
        if self.min is not None:
            ret = ret and (val >= self.min)
        if self.max is not None:
            ret = ret and (val <= self.max)
        return ret

    def __iter__(self):
        low = self.min
        if low is None:
            low = "-inf"
        high = self.max
        if high is None:
            high = "+inf"
        L1 = self.type
        L2 = " {} <= x <= {}".format(low, high)
        return iter((L1, L2))

def prepare_storage(profile_dir:str):
    storage_dir = os.path.join(profile_dir, ".rsssummarizer")

    if os.path.isdir(storage_dir) == False:
        os.mkdir(storage_dir)

    return storage_dir

def prepare_snapshot_dir(storage_dir:str):
    snapshot_dir = os.path.join(storage_dir, "snapshots")

    if os.path.isdir(snapshot_dir) == False:
        os.mkdir(snapshot_dir)

    return snapshot_dir

def prepare_vectored_dir(storage_dir:str):
    vector_dir = os.path.join(storage_dir, "vectors")

    if os.path.isdir(vector_dir) == False:
        os.mkdir(vector_dir)

    return vector_dir

def prepare_model_dir(storage_dir:str):
    model_dir = os.path.join(storage_dir, "models")

    if os.path.isdir(model_dir) == False:
        os.mkdir(model_dir)

    return model_dir

def prepare_fitted_dir(storage_dir:str):
    fitted_dir = os.path.join(storage_dir, "fitted")

    if os.path.isdir(fitted_dir) == False:
        os.mkdir(fitted_dir)

    return fitted_dir

def main(logger:logging.Logger):
    profile_dir = os.path.expanduser('~')

    storage_dir = prepare_storage(profile_dir)
    snapshot_dir = prepare_snapshot_dir(storage_dir)
    vector_dir = prepare_vectored_dir(storage_dir)
    model_dir = prepare_model_dir(storage_dir)
    fitted_dir = prepare_fitted_dir(storage_dir)

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        dotenv_path = join(base_path, 'rsssummarizer.env')
        load_dotenv(dotenv_path)
    else:
        load_dotenv(verbose=True)

    parser = argparse.ArgumentParser(description='Fetch and display information from FreshRSS and Gemini API.')
    parser.add_argument('command', type=str, help='The name of the model to search for.', choices=['vectorize', 'modeling', 'fit'])
    parser.add_argument('--log_level', type=str, choices=['DEBUG', "INFO"], default="DEBUG", help='Log Level')
    parser.add_argument('--remove_snap', action='store_true', help='Remove snapshot after vectorize')
    parser.add_argument('--model_name', type=str, default='umap_model', help='Modeling file name')
    parser.add_argument('--min_dist', type=float, default=0.1, choices=range_check(low_limit=0, high_limit=1.0))
    parser.add_argument('--n_neighbors', type=int, default=5, choices=range_check(low_limit=2))
    parser.add_argument('--metric', type=str, default='cosine', choices=['euclidean', 'cosine'])

    args = parser.parse_args()

    log_level = args.log_level

    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)

    embedding_model = os.environ.get("EMBEDDING_MODEL", "")
    embedding_model_url = os.environ.get("EMBEDDING_MODEL_URL", "http://localhost:11434")
    embedding_api_key = os.environ.get("EMBEDDING_API_KEY", None)
    embedding_method = os.environ.get("EMBEDDING_METHOD", "ollama")

    if args.command == "vectorize":
        vectorize(logger, snapshot_dir, vector_dir, embedding_model, embedding_model_url, embedding_method)
    elif args.command == "modeling":
        vectors_store = []
        for vector_file in glob.glob(os.path.join(vector_dir, "*.csv")):
            df = pd.read_csv(vector_file)
            logger.info(f"Analytics for {vector_file}:")

            df['vector_list'] = df['vector'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else None)
            df['vector_np'] = df['vector_list'].apply(np.array)

            vectors = df['vector_np'].to_list()
            vectors_store += [v for v in vectors if v is not None]

        reducer = umap.UMAP(n_neighbors=args.n_neighbors, min_dist=args.min_dist, n_components=2, metric=args.metric)
        reducer.fit(vectors_store)

        with open(os.path.join(model_dir, args.model_name + ".pkl"), "wb") as f:
            pickle.dump(reducer, f)
    elif args.command == "fit":

        with open(os.path.join(model_dir, args.model_name + ".pkl"), "rb") as f:
            reducer = pickle.load(f)

        logger.info("UMAP model loaded successfully.")
        for vector_file in glob.glob(os.path.join(vector_dir, "*.csv")):
            output_path = os.path.join(fitted_dir, os.path.basename(vector_file))

            df = pd.read_csv(vector_file)
            logger.info(f"Fitting for {vector_file}:")

            df['vector_list'] = df['vector'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else None)
            df['vector_np'] = df['vector_list'].apply(np.array)

            vectors = df['vector_np'].to_list()
            vectors_store = [v for v in vectors if v is not None]

            if len(vectors_store) == 0:
                logger.warning(f"No valid vectors found in {vector_file}. Skipping.")
                continue

            embedding_2d = reducer.transform(vectors_store)
            df_valid = df[df['vector_np'].notnull()].copy()
            df_valid['x'] = embedding_2d[:, 0]
            df_valid['y'] = embedding_2d[:, 1]

            df_shaped = df_valid[['title', 'link', 'issued', 'is_read', 'is_saved', 'x', 'y']]


            df_shaped.to_csv(output_path, index=False)
            logger.info(f"Fitted data saved to {output_path}.")

def vectorize(logger, snapshot_dir, vector_dir, embedding_model, embedding_model_url, embedding_method):
    if embedding_method == "ollama":
        logger.info(f"Using Ollama Embedding Model: {embedding_model} at {embedding_model_url}")
        embeddings = OllamaEmbeddings(model=embedding_model, base_url=embedding_model_url)
    else:
        raise ValueError(f"Unsupported embedding model method: {embedding_method}")

    for snapshot in tqdm(glob.glob(os.path.join(snapshot_dir, "*.json")), desc="Processing snapshots", unit="file"):
        logger.info(f"Processing snapshot: {snapshot}")
        vector_path = os.path.join(vector_dir, os.path.basename(snapshot).replace(".json", ".csv"))

        if not os.path.exists(vector_path):

            with open(snapshot, "r", encoding="utf-8") as f:
                data = pd.read_json(f)

            logger.info(f"Number of texts to embed: {len(data)}")

            vectors = [None] * len(data)

            embedding_execution(logger, embeddings, data, vectors)

            if len(vectors) != len(data):
                logger.error("Length of vectors does not match length of data. Skipping this snapshot.")
                continue

            data['vector'] = vectors
            data.to_csv(vector_path, index=False)
            logger.info(f"Successfully embedded {len(vectors)} texts.")
        else:
            logger.info("skip vectorize due to file exists.")

def embedding_execution(logger, embeddings, data, vectors):
    for index, row in tqdm(data.iterrows(), desc="Embedding texts", total=len(data), unit="text"):
        try:
            vector = embeddings.embed_query(row["title"])
            vectors[index] = vector
        except Exception as e:
            logger.error(f"Error embedding text: {row['title']}. Error: {e}")
            vectors[index] = None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    main(logger=logger)
