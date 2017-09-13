import urllib2
from lxml import html


class Message():
    def __init__(self):
        pass


class SiteParser(object):
    cache = {}
    is_media_parser = False

    def __init__(self, base_url):
        self.base_url = base_url

    def parse_page(self, url):
        if url not in self.cache:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            page = opener.open(url)
            page = html.parse(page)
            self.cache[url] = page
        return self.cache[url]

    def get_title(self):
        """

        :rtype: str
        """
        return ""

    def get_messages(self):
        """

        :rtype: list of Message
        """
        return []


class ForumParser(SiteParser):
    limit = 300

    def get_title(self):
        page = self.parse_page(self.base_url)
        return self.get_page_title(page)

    def get_messages(self):
        self.messages = []
        m_count = 0

        last_page = self.get_page_count()
        for page in xrange(last_page, 0, -1):
            if m_count >= self.limit:
                self.messages = self.messages[-self.limit:]
                break
            page_url = self.build_page_url(page)
            page = self.parse_page(page_url)
            messages = self.get_messages_for_page(page, page_url)
            m_count += len(messages)
            self.messages = messages + self.messages

        return reversed(self.messages)

    def get_page_count(self):
        return int(self.get_last_page(self.parse_page(self.base_url)))


class MediaParser(SiteParser):
    is_media_parser = True
