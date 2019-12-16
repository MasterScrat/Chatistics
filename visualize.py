import argparse
import sys
import logging.config
from parsers.config import config

USAGE_DESC = """
python visualize.py <command> [<args>]

Available commands:
  breakdown        Visualize breakdown of messages
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

    def breakdown(self):
        from visualizers.breakdown import main
        platforms = ['telegram', 'whatsapp', 'messenger', 'hangouts']
        parser = ArgParseDefault(description='Visualize breakdown of messages')
        parser.add_argument('-p', '--platforms', default=platforms, choices=platforms, nargs='+', help='Use data only from certain platforms')
        parser.add_argument('--as-density', dest='as_density', action='store_true', help='Plots densities instead of histograms')
        parser.add_argument('-n', '--number-senders', dest='top_n', type=int, default=10, help= 'Limit the number of different senders to consider, ordered by number of messages sent')
        parser.add_argument('-b', '--bin-width', dest='bin_width', type=int, default=25, help='bin width for histograms')
        parser.add_argument('--filter-conversation', dest='filter_conversation', nargs='+', default=[], help='Limit by conversations with this person/group')
        parser.add_argument('--remove-conversation', dest='remove_conversation', nargs='+', default=[], help='Remove messages by these senders/groups')
        parser.add_argument('--remove-sender', dest='remove_sender', nargs='+', default=[], help='Remove all messages by this sender')
        args = parser.parse_args(sys.argv[2:])
        main(**vars(args))


if __name__ == '__main__':
    ArgParse()
