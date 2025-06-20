import os
import sys
from os.path import join, dirname
from FreshRSSAggregator import client
from dotenv import load_dotenv
import logging
import google.generativeai as genai
import datetime
import argparse
from rich import pretty, print
from rich.console import Console
from rich.markdown import Markdown
from RSSInfra.Summarizer import gemini_summarizer, gemini_summarizer_ex
from RSSInfra.Article import article
from RSSInfra.Fetchers import freshfeed_client
from tinydb import TinyDB, Query
from typing import TypedDict, Optional

logger = None

class LatestRecord(TypedDict):
    name: str  # 必ず 'latest'
    now: str   # ISOフォーマットの時刻文字列
    hoursDelta: int
    maxItems: int
    response: dict # GeminiResult.__dict__ が dict なので dict で定義
    custom_prompt: Optional[str] # custom_prompt は Optional にする

def prepair_storage(profile_dir:str):
    storage_dir = os.path.join(profile_dir, ".rsssummarizer")

    if os.path.isdir(storage_dir) == False:
        os.mkdir(storage_dir)
    
    return storage_dir

def main(logger:logging.Logger):
    console = Console()

    profile_dir = os.path.expanduser('~')

    storage_dir = prepair_storage(profile_dir)

    profile_store = TinyDB(os.path.join(storage_dir, "rsssummarizer.db"))

    load_dotenv(verbose=True)

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        dotenv_path = join(base_path, 'rsssummarizer.env')
    else:  # 通常のスクリプト実行時
        base_path = os.path.dirname(__file__)
        dotenv_path = join(base_path, '.env')

    load_dotenv(dotenv_path)

    parser = argparse.ArgumentParser(description='Fetch and display information from FreshRSS and Gemini API.')
    parser.add_argument('--delta_hours', type=int, default=24, help='Number of hours to fetch data from.')
    parser.add_argument('--max_items', type=int, default=20, help='Number of items to extract')
    parser.add_argument('--custom_prompt', type=str, default=None, help='Custom Prompt')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', "INFO"], default="DEBUG", help='Log Level')

    args = parser.parse_args()

    log_level = args.log_level

    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)

    que = Query()
    latest_record: Optional[LatestRecord] = profile_store.get(que.name == 'latest')

    now = datetime.datetime.now()
    lapped_now = now.replace(minute=0, second=0, microsecond=0)

    response = None # 最終的な要約結果を格納する変数
    should_fetch_and_summarize = True # 要約を再生成する必要があるかどうかのフラグ

    if latest_record:
        try:
            stored_now = datetime.datetime.fromisoformat(latest_record['now'])
            stored_response_text = latest_record['response']['text']
            stored_hours_delta = latest_record.get('hoursDelta') # 存在しない場合を考慮
            stored_max_items = latest_record.get('maxItems') # 存在しない場合を考慮
            stored_custom_prompt = latest_record.get('custom_prompt') # 存在しない場合を考慮

            # キャッシュが有効かどうかの判定
            if (stored_now.year == lapped_now.year and
                stored_now.month == lapped_now.month and
                stored_now.hour == lapped_now.hour and
                stored_hours_delta == args.delta_hours and
                stored_max_items == args.max_items and
                stored_custom_prompt == args.custom_prompt):

                response = gemini_summarizer_ex.GeminiResult(stored_response_text)
                should_fetch_and_summarize = False
                if logger:
                    logger.info("キャッシュされた要約結果を使用します。")
            else:
                if logger:
                    logger.info("キャッシュ条件が一致しないため、要約を再生成します。")
        except KeyError as e:
            # 古いキャッシュ形式などで必要なキーが存在しない場合
            if logger:
                logger.warning(f"キャッシュデータの形式が不適切です。再生成します。エラー: {e}")
            should_fetch_and_summarize = True # 再生成を強制

    if should_fetch_and_summarize:
        summarizer = gemini_summarizer_ex.GeminiSummarizer(None, None)

        rssc = freshfeed_client.FreshFeedClient(os.environ.get("HOST"), os.environ.get("USERNAME"), os.environ.get("PASSWORD"), logger=logger)
        unreads = rssc.Fetch()
        filtered_items = unreads.FilterItemsByHoursDelta(hoursDelta=args.delta_hours, now=now)

        # 要約する記事がない場合のハンドリングを強化
        if filtered_items and filtered_items.list:
            response = summarizer.summarize(filtered_items, args.max_items, custom_prompt=args.custom_prompt)
        else:
            response = gemini_summarizer_ex.GeminiResult("要約するニュースはありません。")
            if logger:
                logger.info("要約する記事が見つかりませんでした。")

    # TinyDB の upsert を使って、存在すれば更新、なければ挿入
    profile_store.upsert(
        {
            "name": "latest",
            "now": now.isoformat(),
            "hoursDelta": args.delta_hours,
            "maxItems": args.max_items,
            "response": response.__dict__,
            "custom_prompt": args.custom_prompt # custom_promptも保存
        },
        que.name == 'latest'
    )

    md = Markdown(response.text)
    
    console.print(md)

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__) # 正しくロガーインスタンスを取得

    main(logger=logger)

