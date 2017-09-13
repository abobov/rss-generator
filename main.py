import sys

from generators import Generator
from plugins import load_plugins


def find_parser(url, args):
    plugins = load_plugins()
    for plugin in plugins:
        if plugin.can_handle(url):
            return plugin.get_parser(url, args)
    raise Exception("No plugin for URL: %s" % url)


def parse_args():
    args_len = len(sys.argv)
    if args_len > 1:
        url = sys.argv[1]
    else:
        raise Exception("First argument: URL")
    args = args_len > 2 and sys.argv[2:]
    return url, args


if __name__ == '__main__':
    url, args = parse_args()
    parser = find_parser(url, args)
    generator = Generator(parser)
    generator.write_xml(sys.stdout)
