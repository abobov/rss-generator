#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import urllib
import urlparse
from lxml import etree

from parsers import Message, ForumParser


def can_handle(url):
    return re.match(r"^https?://forum\.awd\.ru/viewtopic", url, re.IGNORECASE)


def get_parser(url, args):
    return BankiRuForumParser(url)


mon = {
    u'янв': '01',
    u'фев': '02',
    u'мар': '03',
    u'апр': '04',
    u'май': '05',
    u'июн': '06',
    u'июл': '07',
    u'авг': '08',
    u'сен': '09',
    u'окт': '10',
    u'ноя': '11',
    u'дек': '12',
}


class BankiRuForumParser(ForumParser):
    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'//*[@id="page-body"]/*[@id and contains(@class, "post")]')
        for msg in msgs:
            user = msg.xpath(r'.//*[@class="author"]/strong/a/text()')[0]
            date = msg.xpath(r'.//*[@class="author"]/text()')[1]
            msg_url = msg.xpath(r'.//*[@class="author"]/a/@href')[0]
            text = msg.xpath(r'.//div[@class="content"]')[0]

            bank_msg = Message()
            bank_msg.title = '%s: %s' % (self.get_title(), user)
            bank_msg.url = self.__build_full_url(msg_url)
            bank_msg.date = self.__parse_date(date)
            bank_msg.text = etree.tostring(text)

            result.append(bank_msg)
        return result

    def get_page_title(self, page):
        return page.xpath(r'//h2/a/text()')[0]

    def build_page_url(self, page_num):
        url = urlparse.urlparse(self.base_url)
        qs = urlparse.parse_qs(url.query)
        qs['start'] = (page_num - 1) * 20
        url = url._replace(query=urllib.urlencode(qs, True))
        return url.geturl()

    def get_last_page(self, page):
        return page.xpath('//*[@class="pagination"]//strong[2]/text()')[0]

    def __parse_date(self, date):
        date = date[3:].strip()
        date = reduce(lambda x, y: x.replace(y, mon[y]), mon, date)
        return datetime.datetime.strptime(date, '%d %m %Y, %H:%M')

    def __build_full_url(self, url_path):
        return urlparse.urljoin(self.base_url, url_path)
