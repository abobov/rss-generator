#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
from lxml import etree

from parsers import Message, ForumParser


def can_handle(url):
    return re.match(r"^https?://[^\.]+\.createaforum\.com/", url, re.IGNORECASE)


def get_parser(url, args):
    return CrateAForumcomParser(url)


class CrateAForumcomParser(ForumParser):
    page_size = 15

    def __parse_date(self, date):
        date = date.strip(u'» ')
        return datetime.datetime.strptime(date, '%B %d, %Y, %I:%M:%S %p')

    def get_messages_for_page(self, page, page_url=None):
        result = []
        msgs = page.xpath(r'//div[@class="post_wrapper"]')
        for msg in msgs:
            user = msg.xpath(r'.//div[@class="poster"]/h4/a/text()')[0]
            date = msg.xpath(r'.//div[@class="keyinfo"]/div[@class="smalltext"]/text()')[1]
            date = self.__parse_date(date)
            msg_url = msg.xpath(r'.//div[@class="keyinfo"]/h5/a/@href')[0]
            text = msg.xpath(r'.//div[@class="post"]/*')[0]

            bank_msg = Message()
            bank_msg.title = '%s: %s' % (self.get_title(), user)
            bank_msg.url = msg_url
            bank_msg.date = date
            bank_msg.text = etree.tostring(text)

            result.append(bank_msg)
        return result

    def get_page_title(self, page):
        topic = page.xpath(r'//*[@id="forumposts"]/div/h3/text()')[2]
        m = re.match(r'\s*Topic:\s*(.+?)\s*\(Read \d+ times\)\s*', topic)
        return m.group(1) if m else topic

    def build_page_url(self, page_num):
        return "%s/%d" % (self.base_url, self.page_size * (page_num - 1))

    def get_last_page(self, page):
        return page.xpath('(//div[contains(@class, "pagelinks")]/a[@class="navPages"])[last()]/text()')[0]
