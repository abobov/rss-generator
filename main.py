#!/usr/bin/env python3
import argparse
import io
import sys
from contextlib import contextmanager

from generators import Generator
from plugins import load_plugins


def find_parser(url, args):
    plugins = load_plugins()
    for plugin in plugins:
        if plugin.can_handle(url):
            return plugin.get_parser(url, args)
    raise Exception("No plugin for URL: %s" % url)


@contextmanager
def smart_open(file=None):
    if file and file != '-':
        fd = io.open(file, mode="wb")
    else:
        fd = sys.stdout.buffer
    try:
        yield fd
    finally:
        if fd is not sys.stdout.buffer:
            fd.close()


if __name__ == '__main__':
    arguments = argparse.ArgumentParser(description="Generate RSS for sites.")
    arguments.add_argument("-o", "--output", default='-',
                           help="output file name (default: stdout)")
    arguments.add_argument("url", metavar="URL", help="site URL")
    arguments.add_argument("parser_args", metavar="ARGS", nargs="*",
                           help="parser specific arguments")
    args = arguments.parse_args()

    parser = find_parser(args.url, args.parser_args)
    generator = Generator(parser)
    with smart_open(args.output) as fd:
        generator.write_xml(fd)
