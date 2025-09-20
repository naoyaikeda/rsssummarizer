from langchain_community.embeddings import OllamaEmbeddings
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)

# Ollama APIのベースURLとモデル名を指定
ollama_base_url = "http://192.168.1.200:11434"
model_name = "hf.co/bartowski/granite-embedding-278m-multilingual-GGUF:IQ3_M"

try:
    # OllamaEmbeddingsインスタンスを作成
    # base_urlとmodelパラメータで接続先とモデルを指定
    embeddings = OllamaEmbeddings(
        model=model_name,
        base_url=ollama_base_url
    )

    # テキストを埋め込みベクトルに変換
    text = "RAGとキャッシュ戦略の比較"
    vector = embeddings.embed_query(text)

    logging.info(f"成功: テキストが埋め込みベクトルに変換されました。")
    logging.info(f"元のテキスト: '{text}'")
    logging.info(f"埋め込みベクトルの次元数: {len(vector)}")
    logging.info(f"最初の5つの要素: {vector[:5]}")

except Exception as e:
    logging.error(f"エラーが発生しました: {e}")
