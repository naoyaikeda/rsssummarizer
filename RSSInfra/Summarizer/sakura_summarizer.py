import os
import logging
import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from RSSInfra.Article import article
from RSSInfra.Summarizer import gemini_summarizer


class SakuraSummarizer():
    def __init__(self, api_key:str, model_name:str):
        self.model_name = model_name
        self.api_key = api_key
        self.llm = None
        self.temperature = None

        if self.api_key == None:
            self.api_key = os.environ.get("API_KEY")

        if self.model_name == None:
            self.model_name = os.environ.get("MODEL_NAME")
        
        if self.temperature == None:
            self.temperature = float(os.environ.get("TEMPERATURE", "0.7"))

        if self.model_name == None:
            raise ValueError("MODEL_NAME must be specified either as a parameter or as an environment variable.")

        self.llm = ChatOpenAI(base_url='https://api.ai.sakura.ad.jp/v1',model = self.model_name, temperature = self.temperature, api_key = self.api_key, max_retries=2, max_tokens=4096)

    def summarize(self, items:article.Articles, max_items = 20, custom_prompt = None):
        if custom_prompt == None:
            prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """あなたは与えられたタイトルのリストを要約するアシスタントです。
                以下のルールに従って、要約とタイトルの列挙をMarkdown形式で出力してください。なお、挨拶や結語などは不要です。

                1. まず、入力されたタイトルの中から特に重要なものを最大{max_items}個、箇条書きで列挙してください。また、タイトルはそれぞれカテゴリー分けしてください。
                2. 次に、列挙したタイトルやその他の情報から、全体のテーマや内容を簡潔に要約してください。
                3. 出力は必ずMarkdown形式で行ってください。
                """),
                ("user", "以下のタイトルリストを要約してください。\n\n{titles}"),
            ]
        )
        else:
            prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """あなたは与えられたタイトルのリストを要約するアシスタントです。
                以下のルールに従って、要約とタイトルの列挙をMarkdown形式で出力してください。なお、挨拶や結語などは不要です。

                1. まず、入力されたタイトルの中から特に重要なものを最大{max_items}個、箇条書きで列挙してください。また、タイトルはそれぞれカテゴリー分けしてください。
                2. 次に、列挙したタイトルやその他の情報から、全体のテーマや内容を簡潔に要約してください。
                3. 出力は必ずMarkdown形式で行ってください。
                {custom_prompt}
                """),
                ("user", "以下のタイトルリストを要約してください。\n\n{titles}"),
            ]
        )

        output_parser = StrOutputParser()

        chain = prompt_template | self.llm | output_parser

        subjects = [ item.subject + "<" + item.link + ">" for item in items.list ]

        str_subjects = "\n".join(subjects)

        response = self.invoke(str_subjects, chain, max_items, custom_prompt)

        return response

    def invoke(self, subjects, chain, max_items, custom_prompt):
        if custom_prompt == None:
            response = chain.invoke({"titles": subjects, "max_items": max_items})
        else:
            response = chain.invoke({"titles": subjects, "max_items": max_items, "custom_prompt": custom_prompt})

        result = gemini_summarizer.GeminiResult(response)

        return result
