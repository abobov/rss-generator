#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import urllib
import urlparse
from lxml import etree

from parsers import Message, ForumParser


RUS_MONTH = {
    u'января': 1,
    u'февраля': 2,
    u'марта': 3,
    u'апреля': 4,
    u'мая': 5,
    u'июня': 6,
    u'июля': 7,
    u'августа': 8,
    u'сентября': 9,
    u'октября': 10,
    u'ноября': 11,
    u'декабря': 12,
}


def can_handle(url):
    return re.match(r"^https?://(www\.)?avito\.ru/", url, re.IGNORECASE)


def get_parser(url, args):
    return AvitoRuParser(url)


def date_string(days=0):
    d = datetime.date.today() - datetime.timedelta(days)
    return d.strftime("%d.%m")


class AvitoRuParser(ForumParser):
    __replace_dates = [
        (u'Сегодня', date_string()),
        (u'Вчера', date_string(1))
    ]

    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'//*[contains(@class, "item_table-description")]')
        for msg in msgs:
            date = msg.xpath(r'.//*[contains(@class, "date")]/text()')[0].strip()
            price = msg.xpath(r'.//*[contains(@class, "about")]/text()')[0].strip()
            msg_title = msg.xpath(r'.//a[@class="item-description-title-link"]')[0]
            msg_url = 'https://www.avito.ru%s' % msg_title.attrib['href']
            title = msg_title.text.strip()

            ad_msg = Message()
            ad_msg.title = '%s [%s]' % (title, price)
            ad_msg.url = msg_url
            ad_msg.date = self.parse_date(date)
            ad_msg.text = etree.tostring(msg)

            result.append(ad_msg)
        return result

    def get_user(self, user):
        return len(user) and user[0].strip() or ''

    def get_page_title(self, page):
        return page.xpath(r'//title/text()')[0]

    def build_page_url(self, page_num):
        url = urlparse.urlparse(self.base_url)
        qs = urlparse.parse_qs(url.query)
        qs['p'] = page_num
        url = url._replace(query=urllib.urlencode(qs, True))
        return url.geturl()

    def get_last_page(self, page):
        return 1

    def parse_date(self, date):
        date = " ".join(date.split())
        for old, new in self.__replace_dates:
            date = date.replace(old, new)
        for m in RUS_MONTH:
            date = date.replace(' %s' % m, '.%.2d ' % RUS_MONTH[m])
        return datetime.datetime.strptime(date, '%d.%m %H:%M')
