import time
from email.utils import formatdate
from xml.etree.ElementTree import SubElement, Element, ElementTree


def rfc2822time(dt=None):
    if dt is None:
        return formatdate()
    return formatdate(time.mktime(dt.timetuple()))


class Generator(object):
    RSS_ENCODING = 'UTF-8'

    def __init__(self, parser):
        """

        :type parser: parsers.SiteParser
        """
        self.parser = parser

    def write_xml(self, out):
        rss, channel = self.__xml_header()
        for msg in self.parser.get_messages():
            self.__xml_item(channel, msg)
        self.__xml_write(rss, out)

    def __xml_write(self, rss, out):
        ElementTree(rss).write(out, encoding='unicode', xml_declaration=True)

    def __xml_item(self, channel, msg):
        item = SubElement(channel, 'item')
        xs = lambda name, value: self.__xml_sub(item, name, value)
        xs("title", msg.title)
        xs("guid", msg.url)
        xs("description", msg.text)
        xs("pubDate", rfc2822time(msg.date))
        if self.parser.is_media_parser:
            enclosure = SubElement(item, 'enclosure')
            enclosure.attrib['url'] = msg.url
            enclosure.attrib['type'] = 'audio/mpeg'
            if msg.size is not None:
                enclosure.attrib['length'] = str(msg.size)
        else:
            xs("link", msg.url)

    def __xml_header(self):
        rss = Element('rss')
        rss.attrib['version'] = '2.0'
        channel = SubElement(rss, 'channel')
        xs = lambda name, value: self.__xml_sub(channel, name, value)
        xs("title", self.parser.get_title())
        xs("description", "")
        xs("link", self.parser.base_url)
        xs("lastBuildDate", rfc2822time())
        return rss, channel

    def __xml_sub(self, parent, name, text=""):
        sub = SubElement(parent, name)
        sub.text = text
