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

logger = None

def main():
    console = Console()

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

    args = parser.parse_args()

    rssc = client.FreshRSSAggregator(os.environ.get("HOST"), os.environ.get("USERNAME"), os.environ.get("PASSWORD"), logger=logger)

    response = rssc.Fetch(hoursDelta=args.delta_hours, gemini_api_key=os.environ.get("GEMINI_API_KEY"), gemini_model_name=os.environ.get("GEMINI_MODEL_NAME"))

    md = Markdown(response.text)
    console.print(md)

if __name__ == "__main__":

    logging.basicConfig()
    logger = logging.getLogger(__name__).setLevel(logging.DEBUG)

    main()
