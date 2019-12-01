import argparse
import sys
import logging.config

USAGE_DESC = """
python parse.py <command> [<args>]

Available commands:
  telegram         Parse logs from telegram
"""


class ArgParseDefault(argparse.ArgumentParser):
    """Simple wrapper which shows defaults in help"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

class ArgParse():
    def __init__(self):
        logging.config.fileConfig('logging.conf')
        parser = ArgParseDefault(
                description='',
                usage=USAGE_DESC)
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(1)
        getattr(self, args.command)()

    def telegram(self):
        from parsers.telegram import main
        parser = ArgParseDefault(description='Parse message logs from telegram')
        args = parser.parse_args(sys.argv[2:])
        main()

if __name__ == '__main__':
    ArgParse()
