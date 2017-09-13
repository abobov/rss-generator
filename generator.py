import time
import urllib2
from email.utils import formatdate
from lxml import html
from xml.etree.ElementTree import tostring, SubElement, Element


def rfc2822time(dt=None):
    if dt is None:
        return formatdate()
    return formatdate(time.mktime(dt.timetuple()))


class Message():
    def __init__(self):
        pass


class Generator(object):
    RSS_ENCODING = 'UTF-8'

    def __init__(self, parser):
        """

        :type parser: SiteParser
        """
        self.parser = parser

    def get_title(self):
        return self.parser.get_title()

    def get_url(self):
        return self.parser.get_url()

    def get_messages(self):
        return self.parser.get_messages()

    def write_xml(self, out):
        rss, channel = self.__xml_header()
        for msg in self.get_messages():
            self.__xml_item(channel, msg)
        self.__xml_write(rss, out)

    def __xml_write(self, rss, out):
        out.write('<?xml version="1.0" encoding="%s"?>' % self.RSS_ENCODING)
        out.write(tostring(rss).encode(self.RSS_ENCODING))

    def __xml_item(self, channel, msg):
        item = SubElement(channel, 'item')
        xs = lambda name, value: self.__xml_sub(item, name, value)
        xs("title", msg.title)
        xs("guid", msg.url)
        xs("link", msg.url)
        xs("description", msg.text)
        xs("pubDate", rfc2822time(msg.date))

    def __xml_header(self):
        rss = Element('rss')
        rss.attrib['version'] = '2.0'
        channel = SubElement(rss, 'channel')
        xs = lambda name, value: self.__xml_sub(channel, name, value)
        xs("title", self.get_title())
        xs("description", "")
        xs("link", self.get_url())
        xs("lastBuildDate", rfc2822time())
        return rss, channel

    def __xml_sub(self, parent, name, text=""):
        sub = SubElement(parent, name)
        sub.text = text


class SiteParser(object):
    cache = {}

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

    def get_url(self):
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
