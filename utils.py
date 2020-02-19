import os
import logging
from parsers.config import config
import pandas as pd
import argparse

log = logging.getLogger(__name__)


class ArgParseDefault(argparse.ArgumentParser):
    """Simple wrapper which shows defaults in help"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, formatter_class=argparse.ArgumentDefaultsHelpFormatter)


def add_load_data_args(parser):
    """Adds common data loader arguments to arg parser"""
    platforms = ['telegram_api', 'telegram_json', 'whatsapp', 'messenger', 'hangouts']
    parser.add_argument('-p', '--platforms', default=platforms, choices=platforms, nargs='+', help='Use data only from certain platforms')
    parser.add_argument('--filter-conversation', dest='filter_conversation', nargs='+', default=[], help='Limit by conversations with this person/group')
    parser.add_argument('--filter-sender', dest='filter_sender', nargs='+', default=[], help='Limit by messages by this sender')
    parser.add_argument('--remove-conversation', dest='remove_conversation', nargs='+', default=[], help='Remove messages by these senders/groups')
    parser.add_argument('--remove-sender', dest='remove_sender', nargs='+', default=[], help='Remove all messages by this sender')
    parser.add_argument('--outgoing-only', dest='outgoing_only', action='store_true', help='Limit by outgoing messages')
    parser.add_argument('--incoming-only', dest='incoming_only', action='store_true', help='Limit by incoming messages')
    parser.add_argument('--lang', nargs='+', default=[], help='Limit by detected languages')
    parser.add_argument('--contains-keyword', dest='contains_keyword', nargs='+', default=[],
                        help='Limit by messages which contain certain keywords (multiple keywords are used with OR logic)')
    return parser


def load_data(args):
    """Load chat log data based on arg parse filter options"""
    # input paths
    if len(args.platforms) == 0:
        log.info('No platforms specified')
        exit(0)
    df = []
    for platform in args.platforms:
        data_path = os.path.join('data', config[platform]['OUTPUT_PICKLE_NAME'])
        if not os.path.isfile(data_path):
            log.info(f'Could not find any data for platform {platform}')
            continue
        log.info(f'Reading data for platform {platform}')
        _df = pd.read_pickle(data_path)
        df.append(_df)
    df = pd.concat(df, axis=0, ignore_index=True)
    original_len = len(df)
    # filtering
    if len(args.filter_conversation) > 0:
        log.info('Filtering by conversation(s) with {}'.format(', '.join(args.filter_conversation)))
        df = df[df['conversationWithName'].isin(args.filter_conversation)]
    if len(args.filter_sender) > 0:
        log.info('Filtering messages by sender(s) {}'.format(', '.join(args.filter_sender)))
        df = df[df['senderName'].isin(args.filter_sender)]
    if len(args.remove_conversation) > 0:
        log.info('Removing conversations with {}'.format(', '.join(args.remove_conversation)))
        df = df[~df['conversationWithName'].isin(args.remove_conversation)]
    if len(args.remove_sender) > 0:
        log.info('Removing messages by {}'.format(', '.join(args.remove_sender)))
        df = df[~df['senderName'].isin(args.remove_sender)]
    if args.incoming_only:
        log.info('Filtering by incoming only')
        df = df[~df['outgoing']]
    if args.outgoing_only:
        log.info('Filtering by outgoing only')
        df = df[df['outgoing']]
    if len(args.lang) > 0:
        log.info('Filtering by languages {}'.format(', '.join(args.lang)))
        df = df[df['language'].isin(args.lang)]
    if len(args.contains_keyword) > 0:
        log.info('Filtering by messages which contain the keyword(s) {}'.format(', '.join(args.contains_keyword)))
        df = df.dropna(subset=['text'])
        df = df[df['text'].str.contains('|'.join(args.contains_keyword))]
    if 'top_n' in args:
        # find top_n interlocutors
        top_interlocutors = df.conversationWithName.value_counts()
        if len(top_interlocutors) <= args.top_n:
            log.info(f'Tried to filter by top {args.top_n:,} but only {len(top_interlocutors):,} conversations present in data')
        else:
            log.info(f'Filtering top {args.top_n:,} conversations from a total of {len(top_interlocutors):,} conversations')
            df = df[df['conversationWithName'].isin(top_interlocutors.iloc[:args.top_n].index)]
    if len(df) > 0:
        log.info(f'Loaded a total of {len(df):,} messages ({original_len - len(df):,} removed by filters)')
    else:
        log.warning(f'With the given filters no messages could be found!')
        exit(-1)
    return df
