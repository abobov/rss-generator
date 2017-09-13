import StringIO
import unittest
from datetime import datetime

from generators import rfc2822time, Generator
from parsers import Message, SiteParser


class TestSiteParser(SiteParser):
    def get_title(self):
        return "Site Title"

    def get_url(self):
        return "http://www.example.com"

    def get_messages(self):
        msg = Message()
        msg.title = "Message Title"
        msg.url = "http://www.example.com"
        msg.text = "Message Text"
        msg.date = datetime.now()
        return [msg]


class GeneratorTest(unittest.TestCase):
    generator = Generator(TestSiteParser())

    def test_write_xml(self):
        out = StringIO.StringIO()
        self.generator.write_xml(out)
        self.assertIsNotNone(out.getvalue())

    def test_rfc2822time_generator(self):
        dt = datetime.fromtimestamp(1505237983)
        self.assertEqual("Tue, 12 Sep 2017 17:39:43 -0000", rfc2822time(dt))
