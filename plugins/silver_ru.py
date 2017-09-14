#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re

from parsers import Message, MediaParser


def can_handle(url):
    return re.match(r"^https?://(www\.)?silver\.ru/programms/[^/]+/Vipuskyprogrammy", url, re.IGNORECASE)


def get_parser(url, args):
    return SilverRuParser(url)


RUS_MONTH = {
    u'января': 0,
    u'февраля': 1,
    u'марта': 2,
    u'апреля': 3,
    u'мая': 4,
    u'июня': 5,
    u'июля': 6,
    u'августа': 7,
    u'сентября': 8,
    u'октября': 9,
    u'ноября': 10,
    u'декабря': 11,
}

RUS_DOW = {
    'Mon': u'Пн',
    'Tue': u'Вт',
    'Wed': u'Ср',
    'Thu': u'Чт',
    'Fri': u'Пт',
    'Sat': u'Сб',
    'Sun': u'Вс',
}


class SilverRuParser(MediaParser):
    def get_title(self):
        page = self.parse_page(self.base_url)
        title = page.xpath(r'//div[@class="blog"]//h3/text()')[0]
        return title.replace(u'Выпуски программы', '').strip(u'«» ')

    def get_messages(self):
        podcasts = []
        page = self.parse_page(self.base_url)
        for program in page.xpath(r'//div[@class="blog"]//h4/a'):
            podcast_url = 'http://silver.ru%s' % program.get('href')
            podcast = self.__parse_podcast(podcast_url)
            if podcast:
                podcasts.append(podcast)
        return podcasts

    def __parse_podcast(self, podcast_url):
        p = self.parse_page(podcast_url)
        media = p.xpath(r'.//div[@class="blog-detail"]//audio')
        if len(media) == 0:
            return None
        media_url = 'http://silver.ru%s' % media[0].get('src')
        size = self.get_file_size(media_url)
        if size is None:
            return None
        episode_name = p.xpath(r'//div[@class="blog-detail"]/div[@class="title"]/h2/text()')[0]
        program_date = self.__decode_date(
            p.xpath(r'.//div[@class="blog-detail"]/div[@class="title"]/span[last()]/text()')[0])
        podcast = Message()
        podcast.date = program_date
        podcast.title = episode_name
        podcast.url = media_url
        podcast.size = size
        return podcast

    def __decode_date(self, date_string):
        for m in RUS_MONTH:
            date_string = date_string.replace(' %s ' % m, '.%.2d.' % RUS_MONTH[m])
        return datetime.datetime.strptime(date_string, '%d.%m.%Y')
