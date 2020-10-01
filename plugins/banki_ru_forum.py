import datetime
import re
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from lxml import etree

from parsers import Message, ForumParser


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
            text = self.unwrap_links(msg.xpath(r'.//div[@class="forum-post-text"]')[0])

            bank_msg = Message()
            bank_msg.title = user
            bank_msg.url = msg_url
            bank_msg.date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')
            bank_msg.text = etree.tostring(text, encoding='unicode')

            result.append(bank_msg)
        return result

    def get_page_title(self, page):
        return page.xpath(r'//h1[@class="topic-page__title"]/text()')[0]

    def build_page_url(self, page_num):
        url = urllib.parse.urlparse(self.base_url)
        qs = urllib.parse.parse_qs(url.query)
        qs['PAGEN_1'] = page_num
        url = url._replace(query=urllib.parse.urlencode(qs, True))
        return url.geturl()

    def get_last_page(self, page):
        return page.xpath('(//li[@class="ui-pagination__item"])[last()]/a/text()')[0]

    def unwrap_links(self, text):
        away_prefix = '/away/?url='
        for link in text.xpath(r'.//a'):
            href = link.get('href')
            if href.startswith(away_prefix):
                real_href = href[len(away_prefix):]
                link.set('href', urllib.parse.unquote(real_href))
        return text
