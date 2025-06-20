import os
import logging
import datetime
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, stop_after_delay
from RSSInfra.Article import article

class GeminiSummarizer():
    def __init__(self, api_key:str, model_name:str):
        self.model_name = model_name
        self.api_key = api_key

        if self.api_key == None:
            self.api_key = os.environ.get("GEMINI_API_KEY")

        if self.model_name == None:
            self.model_name = os.environ.get("GEMINI_MODEL_NAME")

        if self.model_name == None:
            self.model_name = "gemini-2.0-flash"


    def summarize(self, items:article.Articles):
        prompts = ['以下のリストに示すニュースを要約してください。']

        for item in items.list:
            prompts.append("- " + item.subject)

        prompt = '\n'.join(prompts)

        response = self.invoke(prompt)

        return response

    @retry(stop=stop_after_attempt(3) | stop_after_delay(15))
    def invoke(self, prompt):
        genai.configure(api_key=self.api_key)
        gemini = genai.GenerativeModel(self.model_name)

        response = gemini.generate_content(prompt)
        return response
