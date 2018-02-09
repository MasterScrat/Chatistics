#!/usr/bin/env python3
import argparse

import pandas as pd
from ggplot import *

from parsers import config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', dest='data_paths', nargs='+', help='chat log data files (pickle files)',
                        required=True)
    parser.add_argument('--plot-density', dest='density', action='store_true',
                        help='plots the message densities (KDE) instead of their count')
    parser.add_argument('-n', '--number-senders', dest='top_n', type=int, default=10,
                        help='number of different senders to consider, ordered by number of messages sent')
    parser.add_argument('-b', '--bin-width', dest='bin_width', type=int, default=25, help='bin width for histograms')
    parser.add_argument('--filter-conversation', dest='filter_conversation', type=str, default=None,
                        help='only keep messages sent in a conversation with this sender')
    parser.add_argument('--filter-sender', dest='filter_sender', type=str, default=None,
                        help='only keep messages sent by this sender')
    parser.add_argument('--remove-sender', dest='remove_sender', type=str, default=None,
                        help='remove messages sent by this sender')
    args = parser.parse_args()
    return args


def load_data(data_paths, filter_conversation=None, filter_sender=None, remove_sender=None, top_n=10):
    # data loading
    df = pd.DataFrame()
    for dataPath in data_paths:
        print('Loading', dataPath, '...')
        df = pd.concat([df, pd.read_pickle(dataPath)])

    df.columns = config.ALL_COLUMNS
    print('Loaded', len(df), 'messages')

    # filtering
    if filter_conversation is not None:
        df = df[df['conversationWithName'] == filter_conversation]

    if filter_sender is not None:
        df = df[df['senderName'] == filter_sender]

    if remove_sender is not None:
        df = df[df['senderName'] != remove_sender]

    # keep only topN interlocutors
    mf = df.groupby(['conversationWithName'], as_index=False) \
        .agg(lambda x: len(x)) \
        .sort_values('timestamp', ascending=False)['conversationWithName'] \
        .head(top_n).to_frame()

    print(mf)

    merged = pd.merge(df, mf, on=['conversationWithName'], how='inner')
    merged = merged[['datetime', 'conversationWithName', 'senderName']]

    print('Number to render:', len(merged))
    print(merged.head())
    return merged


def render(data, bin_width, plot_density=False):
    if plot_density:
        plot = ggplot(data, aes(x='datetime', color='conversationWithName')) \
               + geom_density() \
               + scale_x_date(labels='%b %Y') \
               + ggtitle('Conversation Densities') \
               + ylab('Density') \
               + xlab('Date')
    else:
        plot = ggplot(data, aes(x='datetime', fill='conversationWithName')) \
               + geom_histogram(alpha=0.6, binwidth=bin_width) \
               + scale_x_date(labels='%b %Y', breaks='6 months') \
               + ggtitle('Message Breakdown') \
               + ylab('Number of Messages') \
               + xlab('Date')

    print(plot)


def main():
    args = parse_arguments()
    data = load_data(
        data_paths=args.data_paths,
        filter_conversation=args.filter_conversation,
        filter_sender=args.filter_sender,
        remove_sender=args.remove_sender,
        top_n=args.top_n,
    )
    render(data, bin_width=args.bin_width, plot_density=args.density)


if __name__ == '__main__':
    main()
