import os
import sys
from os.path import join, dirname
import datetime
import argparse
import logging
from typing import TypedDict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from rich import pretty, print
from rich.console import Console
from rich.markdown import Markdown
from tinydb import TinyDB, Query
from RSSInfra.Summarizer import gemini_summarizer, sakura_summarizer, openai_summarizer, custom_summarizer
from RSSInfra.Article import article
from RSSInfra.Fetchers import freshfeed_client
from urllib.parse import urlparse

logger = None

class LatestRecord(TypedDict):
    name: str  # 必ず 'latest'
    now: str   # ISOフォーマットの時刻文字列
    hoursDelta: int
    maxItems: int
    response: dict # GeminiResult.__dict__ が dict なので dict で定義
    custom_prompt: Optional[str] # custom_prompt は Optional にする

def prepare_storage(profile_dir:str):
    storage_dir = os.path.join(profile_dir, ".rsssummarizer")

    if os.path.isdir(storage_dir) == False:
        os.mkdir(storage_dir)

    return storage_dir

def main(logger:logging.Logger):
    console = Console()

    profile_dir = os.path.expanduser('~')

    storage_dir = prepare_storage(profile_dir)

    profile_store = TinyDB(os.path.join(storage_dir, "rsssummarizer.db"))

    if getattr(sys, 'frozen', False):
        # PyInstallerで実行されている場合、実行ファイルと同じディレクトリにあるrsssummarizer.envを読み込む
        base_path = os.path.dirname(sys.executable)
        dotenv_path = join(base_path, 'rsssummarizer.env')
        load_dotenv(dotenv_path)
    else:
        # 通常のスクリプトとして実行されている場合、.envファイルを読み込む
        load_dotenv(verbose=True)

    parser = argparse.ArgumentParser(description='Fetch and display information from FreshRSS and Gemini API.')
    parser.add_argument('--delta_hours', type=int, default=None, help='Number of hours to fetch data from.')
    parser.add_argument('--max_items', type=int, default=20, help='Number of items to extract')
    parser.add_argument('--custom_prompt', type=str, default=None, help='Custom Prompt')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', "INFO"], default="DEBUG", help='Log Level')
    parser.add_argument('--clip', action='store_true', help='Save the summary to a file.')
    parser.add_argument('--clip_dir', type=str, default=None, help='Directory to save the summary file.')
    parser.add_argument('--clip_name', type=str, default=None, help='Filename pattern for the summary file.')
    parser.add_argument('--clip_title', type=str, default=None, help='Title for the summary file.')
    parser.add_argument('--tags', type=str, nargs='+', default=['rss', 'summary'], help='Tags for the summary file.')

    args = parser.parse_args()

    max_items = None
    if os.getenv("MAX_ITEMS"):
        max_items = int(os.getenv("MAX_ITEMS"))
    
    delta_hours = None
    if os.getenv("DELTA_HOURS"):
        delta_hours = int(os.getenv("DELTA_HOURS"))
    if args.delta_hours:
        delta_hours = args.delta_hours

    log_level = args.log_level

    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)

    if delta_hours == None:
        delta_hours = 24

    logging.debug(f"Delta Hours: {delta_hours}, Max Items: {max_items}")

    if max_items == None:
        max_items = args.max_items

    custom_prompt = None
    if os.getenv("CUSTOM_PROMPT"):
        custom_prompt = os.getenv("CUSTOM_PROMPT")

    if custom_prompt == None:
        custom_prompt = args.custom_prompt

    summarizer_method = os.getenv("SUMMARIZE_METHOD")

    clip_dir = os.getenv("CLIP_DIR")
    if args.clip_dir:
        clip_dir = args.clip_dir
    if not clip_dir:
        clip_dir = os.path.join(storage_dir, "clips")

    clip_name = os.getenv("CLIP_NAME")
    if args.clip_name:
        clip_name = args.clip_name
    if not clip_name:
        clip_name = "%Y-%m-%d-%H.md"

    clip_title = os.getenv("CLIP_TITLE")
    if args.clip_title:
        clip_title = args.clip_title

    tags = args.tags

    que = Query()
    latest_record: Optional[LatestRecord] = profile_store.get(que.name == 'latest')

    now = datetime.datetime.now()
    lapped_now = now.replace(minute=0, second=0, microsecond=0)

    response = None # 最終的な要約結果を格納する変数
    should_fetch_and_summarize = True # 要約を再生成する必要があるかどうかのフラグ
    fetched_slds = [] # クリップ処理用に必ず定義しておく

    if latest_record:
        try:
            stored_now = datetime.datetime.fromisoformat(latest_record['now'])
            stored_response_text = latest_record['response']['text']
            stored_hours_delta = latest_record.get('hoursDelta') # 存在しない場合を考慮
            stored_max_items = latest_record.get('maxItems') # 存在しない場合を考慮
            stored_custom_prompt = latest_record.get('custom_prompt') # 存在しない場合を考慮
            stored_summarize_method = latest_record.get('summarize_method', 'gemini') # 存在しない場合を考慮

            logging.debug(f"前回の要約日時: {stored_now}, 現在時刻: {now}, ラップされた現在時刻: {lapped_now}")
            logging.debug(f"前回の要約条件 - hoursDelta: {stored_hours_delta}, maxItems: {stored_max_items}, custom_prompt: {stored_custom_prompt}")
            logging.debug(f"現在の要約条件 - hoursDelta: {args.delta_hours}, maxItems: {max_items}, custom_prompt: {custom_prompt}")

            # キャッシュが有効かどうかの判定
            if (stored_now.year == lapped_now.year and
                stored_now.month == lapped_now.month and
                stored_now.hour == lapped_now.hour and
                stored_hours_delta == delta_hours and
                stored_max_items == max_items and
                stored_summarize_method == summarizer_method and
                stored_custom_prompt == custom_prompt):

                response = gemini_summarizer.GeminiResult(stored_response_text)
                should_fetch_and_summarize = False
                # キャッシュからホスト情報を復元（保存していれば）
                if 'hosts_summarized' in latest_record:
                    fetched_slds = latest_record['hosts_summarized']
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
        summarizer = None
        if summarizer_method == 'gemini':
            summarizer = gemini_summarizer.GeminiSummarizer(None, None)
        elif summarizer_method == 'sakura':
            summarizer = sakura_summarizer.SakuraSummarizer(None, None)
        elif summarizer_method == 'openai':
            summarizer = openai_summarizer.OpenAISummarizer(None, None)
        elif summarizer_method == 'custom':
            summarizer = custom_summarizer.CustomSummarizer(None, None)
        else:
            if logger:
                logger.info("要約方法が指定されていないか、認識されません。'gemini'を使用します。")
            summarizer = gemini_summarizer.GeminiSummarizer(None, None)

        rssc = freshfeed_client.FreshFeedClient(os.environ.get("HOST"), os.environ.get("USERNAME"), os.environ.get("PASSWORD"), logger=logger)
        windowed = rssc.Fetch(delta_hours)
        filtered_items = windowed.FilterItemsUnreads()
        fetched_urls = [item.link for item in filtered_items.list if hasattr(item, "link")]
        fetched_slds = sorted(set(
            urlparse(url).hostname.split('.')[-2]
            for url in fetched_urls
            if urlparse(url).hostname is not None and len(urlparse(url).hostname.split('.')) >= 2
        ))

        # 要約する記事がない場合のハンドリングを強化
        if filtered_items and filtered_items.list:
            if summarizer_method == "gemini":
                response = summarizer.summarize(filtered_items, max_items, custom_prompt=custom_prompt)
            if summarizer_method == "sakura":
                response = summarizer.summarize(filtered_items, max_items, custom_prompt=custom_prompt)
            if summarizer_method == "openai":
                response = summarizer.summarize(filtered_items, max_items, custom_prompt=custom_prompt)
            if summarizer_method == "custom":
                response = summarizer.summarize(filtered_items, max_items, custom_prompt=custom_prompt) 
            else:
                response = summarizer.summarize(filtered_items, max_items, custom_prompt=custom_prompt)
        else:
            if logger:
                logger.info("要約する記事が見つかりませんでした。")

    profile_store.upsert(
        {
            "summarize_method": summarizer_method,
            "name": "latest",
            "now": now.isoformat(),
            "hoursDelta": delta_hours,
            "maxItems": max_items,
            "response": response.__dict__,
            "custom_prompt": custom_prompt, # custom_promptも保存
            "hosts_summarized": fetched_slds # ホスト情報もキャッシュに保存
        },
        que.name == 'latest'
    )

    md = Markdown(response.text)

    console.print(md)

    if args.clip:
        # Format the filename
        filename = lapped_now.strftime(clip_name)
        filepath = os.path.join(clip_dir, filename)

        # Check if file exists
        if os.path.exists(filepath):
            if logger:
                logger.info(f"Clip file already exists for this hour: {filepath}. Skipping.")
        else:
            # Create directory if it doesn't exist
            os.makedirs(clip_dir, exist_ok=True)

            # Fetch hosts from the articles
            joined_tags = sorted(set(tags + fetched_slds))

            # Prepare tags for frontmatter
            tags_yaml = ", ".join(joined_tags)

            # Generate YAML frontmatter
            date_iso = lapped_now.astimezone().isoformat()
            frontmatter = f"""---
tags: [{tags_yaml}]
date: {date_iso}
max_items: {max_items}
hours_delta: {args.delta_hours}
custom_prompt: {custom_prompt if custom_prompt else "None"}
hosts_summarized: [{", ".join(fetched_slds)}]
summarize_method: {summarizer_method}
source: FreshRSS + {summarizer_method}
---

"""
            # Prepare title
            title_text = ""
            if clip_title:
                title_text = "# " + lapped_now.strftime(clip_title) + "\n\n"
            else:
                # Use filename (without extension) as default title
                base_filename = os.path.splitext(filename)[0]
                title_text = "# " + base_filename + "\n\n"

            content_to_write = frontmatter + title_text + response.text

            # Write the file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_to_write)
            if logger:
                logger.info(f"Summary clipped to: {filepath}")

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__) # 正しくロガーインスタンスを取得

    main(logger=logger)

