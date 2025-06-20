import datetime

class Article:
    subject = None
    created_on_time = None

    def __init__(self, subject:str, created_on_time):
        self.subject = subject
        self.created_on_time = created_on_time

class Articles:
    list = []

    def __init__(self, list = None):
        self.list = []

        if list:
            for item in list:
                self.list.append(Article(item.title, item.created_on_time))

    def FilterItemsByHoursDelta(self, hoursDelta:int, now:datetime.datetime):
        pass