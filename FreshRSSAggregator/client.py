import os
from freshrss_api import FreshRSSAPI
import logging
import datetime
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, stop_after_delay

class FreshRSSAggregator():
    api_client = None
    logger = None

    def __init__(
                self,
                host: str = None,
                username: str = None,
                password: str = None,
                verify_ssl: bool = True,
                verbose: bool = False,
                logger = None
                ):

        self.api_client = FreshRSSAPI(host, username, password, verify_ssl, verbose)
        self.logger = logger

        if self.logger:
            self.logger.debug("Initialized")

    def Fetch(self, hoursDelta: int = 24, gemini_api_key:str = None, gemini_model_name:str = None):
        if self.logger:
            self.logger.debug("Fetch start")

        if gemini_api_key == None:
            gemini_api_key = os.environ.get("GEMINI_API_KEY")

        if gemini_model_name == None:
            gemini_model_name = os.environ.get("GEMINI_MODEL_NAME")

        unread_items = None
        unread_items = self.GetUnreads()
        if gemini_model_name == None:
            gemini_model_name = "gemini-2.0-flash"

        filtered_items = self.FilterItems(hoursDelta, unread_items)

        prompts = ['以下のリストに示すニュースを要約してください。']
        for item in filtered_items:
            prompts.append("- " + item.title)

        prompt = '\n'.join(prompts)

        response = self.call_gemini(prompt, gemini_api_key, gemini_model_name)

        return(response)

    @retry(stop=stop_after_attempt(3) | stop_after_delay(15))
    def call_gemini(self, prompt, gemini_api_key, gemini_model_name):
        genai.configure(api_key=gemini_api_key)
        gemini_pro = genai.GenerativeModel(gemini_model_name)

        response = gemini_pro.generate_content(prompt)
        return response

    @retry(stop=stop_after_attempt(3))
    def GetUnreads(self):
        if self.logger:
            self.logger.debug("Fetch one")

        unread_items = self.api_client.get_unreads()
        return unread_items

    def FilterItems(self, hoursDelta:int, unread_items):
        now = datetime.datetime.now()
        threshold_time = now - datetime.timedelta(hours=hoursDelta)

        filtered_items = [
            item for item in unread_items
            if datetime.datetime.fromtimestamp(item.created_on_time) > threshold_time]

        return filtered_items
