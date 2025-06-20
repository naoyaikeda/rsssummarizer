import os
from freshrss_api import FreshRSSAPI
import logging
import datetime
# from RSSInfra.Summarizer import gemini_summarizer, gemini_summarizer_ex
from RSSInfra.Article import article
from tenacity import retry, stop_after_attempt, stop_after_delay

class FreshFeedClient():
    api_client = None
    logger = None
    summarizer = None

    def __init__(
                self,
                host: str = None,
                username: str = None,
                password: str = None,
                verify_ssl: bool = True,
                verbose: bool = False,
                logger = None,
                ):

        self.api_client = FreshRSSAPI(host, username, password, verify_ssl, verbose)
        self.logger = logger

        if self.logger:
            self.logger.debug("Initialized")

    def Fetch(self):
        if self.logger:
            self.logger.debug("Fetch start")

        unread_items = None
        unread_items = self.GetUnreads()

        articles = article.Articles(list=unread_items)

        return articles

    @retry(stop=stop_after_attempt(3))
    def GetUnreads(self):
        if self.logger:
            self.logger.debug("Fetch one")

        unread_items = self.api_client.get_unreads()
        return unread_items
