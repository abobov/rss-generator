import StringIO
import unittest
from datetime import datetime

from generator import rfc2822time, Generator, SiteParser, Message


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

    def test_get_title(self):
        self.assertEqual("Site Title", self.generator.get_title())

    def test_get_url(self):
        self.assertEqual("http://www.example.com", self.generator.get_url())

    def test_last_messages(self):
        messages = self.generator.get_messages()
        self.assertEqual(1, len(messages))

    def test_write_xml(self):
        out = StringIO.StringIO()
        self.generator.write_xml(out)
        self.assertIsNotNone(out.getvalue())

    def test_rfc2822time_generator(self):
        dt = datetime.fromtimestamp(1505237983)
        self.assertEqual("Tue, 12 Sep 2017 17:39:43 -0000", rfc2822time(dt))
