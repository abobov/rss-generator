#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import urllib
import urlparse
from lxml import etree

from generator import Message, ForumParser


def can_handle(url):
    return re.match(r"^https?://forum\.onliner\.by/", url, re.IGNORECASE)


def get_parser(url, args):
    return ForumOnlinerByParser(url)


mon = {
    u'января': '01',
    u'февраля': '02',
    u'марта': '03',
    u'апреля': '04',
    u'мая': '05',
    u'июня': '06',
    u'июля': '07',
    u'августа': '08',
    u'сентября': '09',
    u'октября': '00',
    u'ноября': '11',
    u'декабря': '12',
}


class ForumOnlinerByParser(ForumParser):
    def get_page_title(self, page):
        return page.xpath(r'//h1[@class="m-title"]/a/text()')[0]

    def get_last_page(self, page):
        return page.xpath('(//ul[contains(@class, "topic-pages-fastnav")]/li[not(@class)])[last()]/a/text()')[0]

    def build_page_url(self, page_num):
        url = urlparse.urlparse(self.base_url)
        qs = urlparse.parse_qs(url.query)
        qs['start'] = (page_num - 1) * 20
        url = url._replace(query=urllib.urlencode(qs, True))
        return url.geturl()

    def get_messages_for_page(self, page, page_url):
        result = []
        msgs = page.xpath(
            r'//ul[@class="b-messages-thread"]/li[contains(@class, "msgpost") and not(contains(@class, "msgfirst"))]')
        for msg in msgs:
            user = msg.xpath(r'.//div[@class="b-mtauthor"]//a[contains(@class, "_name")]/@title')[0]
            date = msg.xpath(r'.//small[@class="msgpost-date"]/span[@title]/text()')[0]
            msg_url = msg.xpath(r'.//small[@class="msgpost-date"]/a/@href')[0]
            text = msg.xpath(r'.//div[@class="content"]')[0]

            date = reduce(lambda x, y: x.replace(y, mon[y]), mon, date)

            msg_url = page_url + msg_url

            bank_msg = Message()
            bank_msg.title = '%s: %s [%s]' % (self.get_title(), user, date)
            bank_msg.url = msg_url
            bank_msg.date = datetime.datetime.strptime(date, '%d %m %Y %H:%M')
            bank_msg.text = etree.tostring(text)

            result.append(bank_msg)
        return result
