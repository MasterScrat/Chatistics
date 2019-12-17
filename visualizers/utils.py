import os
import time
import logging
from parsers.config import config
import pandas as pd
import json

log = logging.getLogger(__name__)

def save_fig(fig, name, output_formats=('png',), dpi=300):
    """Save figure with timestamps"""
    date = time.strftime('%Y%m%d')
    ts = int(time.time() * 1000)
    for fmt in output_formats:
        save_name = os.path.join('plots', f'{name}_{ts}.{fmt}')
        log.info(f'Saving figure as {save_name}')
        fig.savefig(save_name, dpi=dpi)

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
    if 'top_n' in args:
        # find top_n interlocutors
        top_interlocutors = df.conversationWithName.value_counts()
        if len(top_interlocutors) <= args.top_n:
            log.info(f'Tried to filter by top {args.top_n:,} but only {len(top_interlocutors):,} conversations present in data')
        else:
            log.info(f'Filtering top {args.top_n:,} conversations from a total of {len(top_interlocutors):,} conversations')
            df = df[df['conversationWithName'].isin(top_interlocutors.iloc[:args.top_n].index)]
    if len(df) > 0:
        log.info(f'Loaded a total of {len(df):,} messages ({original_len-len(df):,} removed by filters)')
    else:
        log.warning(f'With the given filters no messages could be found!')
        exit(-1)
    return df

def get_stopwords(stopword_paths):
    """Load stopwords given a stopword path"""
    stopwords = []
    for stopword_path in stopword_paths:
        log.info(f'Loading stopwords from {stopword_path}...')
        with open(stopword_path, 'r') as f:
            stopword_data = json.load(f)
        stopwords.extend(stopword_data)
    stopwords = list(set(stopwords))
    log.info(f'Loaded {len(stopwords):,} stopwords')
    return stopwords

