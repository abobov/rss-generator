#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re

from parsers import Message, MediaParser


def can_handle(url):
    return re.match(r"^https?://(www\.)?govoritmoskva\.ru/broadcasts/", url, re.IGNORECASE)


def get_parser(url, args):
    return GovorimoskvaRuParser(url)


RUS_DOW = {
    'Mon': u'Пн',
    'Tue': u'Вт',
    'Wed': u'Ср',
    'Thu': u'Чт',
    'Fri': u'Пт',
    'Sat': u'Сб',
    'Sun': u'Вс',
}


class GovorimoskvaRuParser(MediaParser):
    def get_title(self):
        page = self.parse_page(self.base_url)
        title = page.xpath(r'//div[@class="oneProgramPage"]//h1/text()')[0]
        return title.replace(u'(16+)', '').strip(u'«» ')

    def get_broadcast_url(self, month=None, year=None):
        if month is None and year is None:
            return self.base_url
        else:
            return r'%s?month=%d&year=%d' % (self.base_url, month, year)

    def episode_name(self, title, date):
        dow = date.strftime('%a')
        return '%s, %s %d' % (title, RUS_DOW.get(dow, dow), date.day)

    def get_messages(self):
        # Fetch page for current and previous month
        today = datetime.date.today()
        prev = today - datetime.timedelta(days=today.day)

        title = self.get_title()

        messages = []
        for date in (today, prev):
            url = self.get_broadcast_url(date.month, date.year)
            page = self.parse_page(url)
            messages += self.podcasts_for_month(page, date, title)
        return messages

    def podcasts_for_month(self, page, date, title):
        podcasts = []
        descr = page.xpath(r'//div[@class="textDescribe"]/p[last()]/text()')[0]
        for program in page.xpath(r'//ul[@class="programList"]/li'):
            media = program.xpath(r'.//a[@download]')
            if len(media) == 0:
                continue
            assert len(media) == 1, 'Should be only one media, by found: %d' % len(media)
            media_url = media[0].get('href')
            if not media_url.startswith('http'):
                media_url = 'http://govoritmoskva.ru/' + media_url
            size = self.get_file_size(media_url)
            if size is not None:
                day = int(program.xpath(r'.//div[@class="time"]/span/text()')[0].split(' ')[0])
                program_date = date.replace(day=day)
                podcast = Message()
                podcast.title = self.episode_name(title, program_date)
                podcast.url = media_url
                podcast.date = program_date
                podcast.text = descr
                podcast.size = size

                podcasts.append(podcast)
        return podcasts
