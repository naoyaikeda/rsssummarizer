import datetime

class Article:
    subject = None
    created_on_time = None

    def __init__(self, subject:str, link:str, created_on_time, is_read = False, is_saved = False):
        self.subject = subject
        self.created_on_time = created_on_time
        self.link = link
        self.is_read = is_read
        self.is_saved = is_saved

class Articles:
    list = []

    def __init__(self):
        self.list = []

    def FilterItemsByHoursDelta(self, hoursDelta:int, now:datetime.datetime):

        threshold_time = now - datetime.timedelta(hours=hoursDelta)

        filtered_items = [
            item for item in self.list
            if datetime.datetime.fromtimestamp(item.created_on_time) > threshold_time]

        return articlesFromListOfArticle(filtered_items)

    def FilterItemsUnreads(self):

        filtered_items = [
            item for item in self.list
            if item.is_read == False]

        return articlesFromListOfArticle(filtered_items)


def articlesFromResponse(list = None):
    articles = Articles()

    if list:
        for item in list:
            articles.list.append(Article(item.title, item.url, item.created_on_time, item.is_read, item.is_saved))

    return articles

def articlesFromListOfArticle(list = None):
    articles = Articles()

    if list:
        for item in list:
            articles.list.append(Article(item.subject, item.link, item.created_on_time, item.is_read, item.is_saved))

    return articles
