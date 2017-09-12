import datetime
import re
import urllib
import urlparse
from lxml import etree

from generator import SiteParser, Message


def can_handle(url):
    return re.match(r"^https?://(www\.)?banki\.ru/forum/", url, re.IGNORECASE)


def get_parser(url, args):
    return BankiRuForumParser(url)


class BankiRuForumParser(SiteParser):
    limit = 300

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
            messages = self.get_messages_for_page(page)
            m_count += len(messages)
            self.messages = messages + self.messages

        return reversed(self.messages)

    def get_messages_for_page(self, page):
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

    def get_url(self):
        return super(BankiRuForumParser, self).get_url()

    def get_title(self):
        page = self.parse_page(self.base_url)
        return page.xpath(r'//h1[@class="topic-page__title"]/text()')[0]

    def build_page_url(self, page_num):
        url = urlparse.urlparse(self.base_url)
        qs = urlparse.parse_qs(url.query)
        qs['PAGEN_1'] = page_num
        url = url._replace(query=urllib.urlencode(qs, True))
        return url.geturl()

    def get_page_count(self):
        page = self.parse_page(self.base_url)
        last_page = page.xpath('(//li[@class="ui-pagination__item"])[last()]/a/text()')[0]
        return int(last_page)
