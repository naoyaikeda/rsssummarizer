import os
from freshrss_api import FreshRSSAPI
import logging
import datetime
from RSSInfra.Article import article
from tenacity import retry, stop_after_attempt, stop_after_delay
from dotenv import load_dotenv
import pickle

load_dotenv(verbose=True)

api_client = FreshRSSAPI(os.environ.get("HOST"), os.environ.get("USERNAME"), os.environ.get("PASSWORD"))

now = datetime.datetime.now()
unreads = api_client.get_items_from_dates(since = now - datetime.timedelta(hours=48), until = now)

articles = article.articlesFromResponse(unreads)
pickle.dump(articles, open("testdata.pkl", "wb"))
