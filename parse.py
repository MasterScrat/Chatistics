import logging.config
import sys

from parsers.config import config
from utils import ArgParseDefault

USAGE_DESC = """
python parse.py <command> [<args>]

Available commands:
  telegram_api     Parse logs from telegram (api)
  telegram_json    Parse logs from telegram (desktop client)
  hangouts         Parse logs from hangouts
  messenger        Parse logs from messenger
  whatsapp         Parse logs from whatsapp
"""


def add_common_parse_arguments(parser):
    parser.add_argument('--own-name', dest='own_name', type=str, default=None, help='Name of the owner of the chat logs, written as in the logs',
                        required=False)
    parser.add_argument('--max', '--max-exported-messages', dest='max', type=int, default=config['MAX_EXPORTED_MESSAGES'],
                        help='Maximum number of messages to export')
    return parser


def str2bool(v):
    return v != 'false'


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

    def telegram_api(self):
        from parsers.telegram_api import main
        parser = ArgParseDefault(description='Parse message logs from Telegram (API)')
        parser = add_common_parse_arguments(parser)
        parser.add_argument('--max-dialog', dest='max_dialog', type=int, default=config['telegram_api']['USER_DIALOG_MESSAGES_LIMIT'],
                            help='Maximum number of messages to export per dialog')
        args = parser.parse_args(sys.argv[2:])
        main(args.own_name, max_exported_messages=args.max, user_dialog_messages_limit=args.max_dialog)

    def telegram_json(self):
        from parsers.telegram_json import main
        parser = ArgParseDefault(description='Parse message logs from Telegram (Desktop Client)')
        parser = add_common_parse_arguments(parser)
        parser.add_argument('-f', '--file-path', dest='file_path', default=config['telegram_json']['DEFAULT_RAW_LOCATION'],
                            help='Path to Telegram chat log file (json file)')
        args = parser.parse_args(sys.argv[2:])
        main(args.own_name, args.file_path, args.max)

    def hangouts(self):
        from parsers.hangouts import main
        parser = ArgParseDefault(description='Parse message logs from Google Hangouts')
        parser = add_common_parse_arguments(parser)
        parser.add_argument('-f', '--file-path', dest='file_path', default=config['hangouts']['DEFAULT_RAW_LOCATION'],
                            help='Path to Hangouts chat log file (json file)')
        args = parser.parse_args(sys.argv[2:])
        main(args.own_name, args.file_path, args.max)

    def messenger(self):
        from parsers.messenger import main
        parser = ArgParseDefault(description='Parse message logs from Facebook Messenger')
        parser = add_common_parse_arguments(parser)
        parser.add_argument('-f', '--file-path', dest='file_path', default=config['messenger']['DEFAULT_RAW_LOCATION'],
                            help='Path to Facebook messenger chat log folder')
        args = parser.parse_args(sys.argv[2:])
        main(args.own_name, args.file_path, args.max)

    def whatsapp(self):
        from parsers.whatsapp import main
        parser = ArgParseDefault(description='Parse message logs from Whatsapp')
        parser = add_common_parse_arguments(parser)
        parser.add_argument('-f', '--file-path', dest='file_path', default=config['whatsapp']['DEFAULT_RAW_LOCATION'],
                            help='Path to Facebook messenger chat log folder')
        parser.add_argument('-i', '--infer-datetime', dest='infer_datetime', type=str2bool, nargs='?',
                            default=True, help='Infer datetime regex for each chat if true')
        args = parser.parse_args(sys.argv[2:])
        main(args.own_name, args.file_path, args.max, args.infer_datetime)


if __name__ == '__main__':
    ArgParse()
