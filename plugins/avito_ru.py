#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from datetime import timedelta
from lxml import etree

from parsers import Message, ForumParser

RUS_MONTH = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}


def can_handle(url):
    return re.match(r"^https?://(www\.)?avito\.ru/", url, re.IGNORECASE)


def get_parser(url, args):
    return AvitoRuParser(url)


def date_string(days=0):
    d = datetime.date.today() - timedelta(days=days)
    return d.strftime("%d.%m")


def date_rel(pattern, date, key):
    match = re.match(pattern, date)
    if match:
        value = int(match.group(1))
        return datetime.datetime.today() - timedelta(**dict([(key, value)]))


class AvitoRuParser(ForumParser):
    __replace_dates = [
        ('Сегодня', date_string()),
        ('Вчера', date_string(days=1)),
    ]

    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'//*[contains(@class, "item_table-description")]')
        for msg in msgs:
            date = msg.xpath(r'.//*[@class="data"]//*[@data-absolute-date]/text()')[0].strip()
            price = msg.xpath(r'.//*[contains(@class, "about")]/text()')[0].strip()
            msg_title = msg.xpath(r'.//a[@class="item-description-title-link"]')[0]
            msg_url = 'https://www.avito.ru%s' % msg_title.attrib['href']
            title = msg_title.text.strip()

            ad_msg = Message()
            ad_msg.title = '%s [%s]' % (title, price)
            ad_msg.url = msg_url
            try:
                ad_msg.date = self.parse_date(date)
            except:
                continue
            ad_msg.text = etree.tostring(msg, encoding='unicode')

            result.append(ad_msg)
        return result

    def get_user(self, user):
        return len(user) and user[0].strip() or ''

    def get_page_title(self, page):
        return page.xpath(r'//title/text()')[0]

    def build_page_url(self, page_num):
        url = urllib.parse.urlparse(self.base_url)
        qs = urllib.parse.parse_qs(url.query)
        qs['p'] = page_num
        url = url._replace(query=urllib.parse.urlencode(qs, True))
        return url.geturl()

    def get_last_page(self, page):
        return 1

    def parse_date(self, date):
        date = " ".join(date.split())

        res = date_rel('(\d+) час(|а|ов) назад', date, 'hours')
        if res:
            return res
        res = date_rel('(\d+) минут(у|а|ы|) назад', date, 'minutes')
        if res:
            return res
        res = date_rel('(\d+) (день|дня|дней) назад', date, 'days')
        if res:
            return res

        parse_date = date
        for old, new in self.__replace_dates:
            parse_date = parse_date.replace(old, new)
        for m in RUS_MONTH:
            parse_date = parse_date.replace(' %s' % m, '.%.2d ' % RUS_MONTH[m])
        try:
            return datetime.datetime.strptime(parse_date, '%d.%m %H:%M')
        except:
            print("Date parse error, input date: '%s'" % date, file=sys.stderr)
            raise
