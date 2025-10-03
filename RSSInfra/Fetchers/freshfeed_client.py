import os
from freshrss_api import FreshRSSAPI
import logging
import datetime
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

    def Fetch(self, delta_hours):
        if self.logger:
            self.logger.debug("Fetch start")

        unread_items = None
        unread_items = self.GetWindowed(delta_hours)

        articles = article.articlesFromResponse(unread_items)

        return articles

    @retry(stop=stop_after_attempt(3))
    def GetWindowed(self, delta_hours):
        if self.logger:
            self.logger.debug("Fetch one")

        now = datetime.datetime.now()
        windowed_items = self.api_client.get_items_from_dates(since = now - datetime.timedelta(hours=delta_hours), until = now)
        return windowed_items
