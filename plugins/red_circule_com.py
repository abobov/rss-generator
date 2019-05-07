#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import sys
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
    return re.match(r"^https?://red-circule\.com/articles", url, re.IGNORECASE)


def get_parser(url, args):
    return RedCircleComParser(url)


class RedCircleComParser(ForumParser):

    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'.//*[starts-with(@class, "articlesPanel--")]//*[starts-with(@class, "item")]')
        for msg in msgs:
            date = msg.xpath(r'.//*[starts-with(@class, "date--")]/text()')[0].strip()
            title = msg.xpath(r'.//*[starts-with(@class, "title--")]/text()')[0].strip()
            link = msg.xpath(r'.//a[starts-with(@class, "titleLink--")]')[0]
            msg_url = 'https://red-circule.com%s' % link.attrib['href']

            ad_msg = Message()
            ad_msg.title = title
            ad_msg.url = msg_url
            try:
                ad_msg.date = self.parse_date(date)
            except:
                continue
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

        parse_date = date
        for m in RUS_MONTH:
            parse_date = parse_date.replace(' %s ' % m, '.%.2d.' % RUS_MONTH[m])
        try:
            return datetime.datetime.strptime(parse_date, '%d.%m.%Y')
        except:
            print >> sys.stderr, "Date parse error, input date: '%s'" % date
            raise
