import argparse
import sys
import logging.config
from utils import ArgParseDefault, add_load_data_args

USAGE_DESC = """
python visualize.py <command> [<args>]

Available commands:
  breakdown        Visualize breakdown of messages
  cloud            Visualize word clouds
"""


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
        parser = ArgParseDefault(description='Visualize breakdown of messages')
        parser = add_load_data_args(parser)
        parser.add_argument('--as-density', dest='as_density', action='store_true', help='Plots individual densities instead of stacked histograms')
        parser.add_argument('-n', '--top-n', dest='top_n', type=int, default=10, help='Only consider the top n conversation partners (by number of messages)')
        parser.add_argument('-b', '--bin-size', dest='bin_size', type=str, default='1M',
                            help='Bin sizes (use the pandas Timedelta abbreviations of the form <number><type> where type can be ‘Y’, ‘M’, ‘W’, ‘D’, ‘days’, ‘day’, ‘hours’, hour’, ‘hr’, ‘h’, ‘m’, ‘minute’, ‘min’, ‘minutes’, ‘T’, ‘S’, ‘seconds’, ‘sec’, ‘second’, ‘ms’, ‘milliseconds’, ‘millisecond’, ‘milli’, ‘millis’, ‘L’, ‘us’, ‘microseconds’, ‘microsecond’, ‘micro’, ‘micros’, ‘U’, ‘ns’, ‘nanoseconds’, ‘nano’, ‘nanos’, ‘nanosecond’, ‘N’).')
        args = parser.parse_args(sys.argv[2:])
        main(args)

    def cloud(self):
        from visualizers.cloud import main
        parser = ArgParseDefault(description='Visualize word clouds')
        parser = add_load_data_args(parser)
        parser.add_argument('-m', '--mask-image', dest='mask_image', type=str, default=None, help='Image to use as mask', required=True)
        parser.add_argument('--sw', '--stopword-paths', dest='stopword_paths', nargs='+', default=['stopwords/en.json'],
                            help='Path to stopword files (JSON format)')
        parser.add_argument('-n', '--num-words', dest='num_words', type=int, default=10000, help='Print up to n words into the cloud')
        parser.add_argument('--density', '--dpi', dest='dpi', type=int, default=300, help='Rendered image DPI')
        args = parser.parse_args(sys.argv[2:])
        main(args)


if __name__ == '__main__':
    ArgParse()
