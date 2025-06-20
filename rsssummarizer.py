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
from tinydb import TinyDB, Query

logger = None

def prepair_storage(profile_dir:str):
    storage_dir = os.path.join(profile_dir, ".rsssummarizer")

    if os.path.isdir(storage_dir) == False:
        os.mkdir(storage_dir)
    
    return storage_dir

def main():
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

    args = parser.parse_args()

    now = datetime.datetime.now()

    summarizer = gemini_summarizer_ex.GeminiSummarizer(None, None)

    rssc = client.FreshRSSAggregator(os.environ.get("HOST"), os.environ.get("USERNAME"), os.environ.get("PASSWORD"), logger=logger, summarizer = summarizer)

    response = rssc.Fetch(hoursDelta=args.delta_hours, max_items=args.max_items, custom_prompt = args.custom_prompt)

    md = Markdown(response.text)
    console.print(md)

if __name__ == "__main__":

    logging.basicConfig()
    logger = logging.getLogger(__name__).setLevel(logging.DEBUG)

    main()
