import datetime
import re
import urllib
import urlparse
from lxml import etree

from generator import Message, ForumParser


def can_handle(url):
    return re.match(r"^https?://(www\.)?banki\.ru/forum/", url, re.IGNORECASE)


def get_parser(url, args):
    return BankiRuForumParser(url)


class BankiRuForumParser(ForumParser):
    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'//div[@class="forum-messages-list"]/div')
        for msg in msgs:
            user = msg.xpath(r'.//div[@class="forum-user-name"]/a/@title')[0]
            date = msg.xpath(r'.//div[@class="forum-post-date"]/span/text()')[0]
            msg_url = msg.xpath(r'.//div[@class="forum-post-number"]/noindex/a/@href')[0]
            text = msg.xpath(r'.//div[@class="forum-post-text"]')[0]

            bank_msg = Message()
            bank_msg.title = '%s: %s [%s]' % (self.get_title(), user, date)
            bank_msg.url = msg_url
            bank_msg.date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')
            bank_msg.text = etree.tostring(text)

            result.append(bank_msg)
        return result

    def get_page_title(self, page):
        return page.xpath(r'//h1[@class="topic-page__title"]/text()')[0]

    def build_page_url(self, page_num):
        url = urlparse.urlparse(self.base_url)
        qs = urlparse.parse_qs(url.query)
        qs['PAGEN_1'] = page_num
        url = url._replace(query=urllib.urlencode(qs, True))
        return url.geturl()

    def get_last_page(self, page):
        return page.xpath('(//li[@class="ui-pagination__item"])[last()]/a/text()')[0]
