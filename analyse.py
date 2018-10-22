#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import warnings
import matplotlib.cbook
import os

import pandas as pd
import sys
from ggplot import *

from parsers import config

# Hides warning from ggplot==0.6.8
# Unfortunately newer versions are too buggy
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


def data_check():
    """
    Ensure that there's literally anyting in the /raw/ directory besides .gitkeep.

    Prompt the user with a friendly reminder if there isn't.
    """

    repo_root = os.path.abspath('.')
    data_dir = os.path.join(repo_root, '', 'raw')

    if len(os.listdir(data_dir)) < 2:
        sys.exit(
            "No messages found. Please copy your messages into the 'raw' directory."
        )

        # now that that check is here we don't need to make data a required argument.
        # we know for a fact that there are files in the correct directory, and so we'll parse everything in there.


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--data',
        dest='data_paths',
        nargs='+',
        help='chat log data files (pickle files)',
    )
    parser.add_argument(
        '--plot-density',
        dest='density',
        action='store_true',
        help='plots the message densities (KDE) instead of their count')
    parser.add_argument(
        '-n',
        '--number-senders',
        dest='top_n',
        type=int,
        default=10,
        help=
        'number of different senders to consider, ordered by number of messages sent'
    )
    parser.add_argument(
        '-b',
        '--bin-width',
        dest='bin_width',
        type=int,
        default=25,
        help='bin width for histograms')
    parser.add_argument(
        '--filter-conversation',
        dest='filter_conversation',
        type=str,
        default=None,
        help='only keep messages sent in a conversation with these senders, separated by comma')
    parser.add_argument(
        '--filter-sender',
        dest='filter_sender',
        type=str,
        default=None,
        help='only keep messages sent by these senders, separated by comma')
    parser.add_argument(
        '--remove-sender',
        dest='remove_sender',
        type=str,
        default=None,
        help='remove messages sent by these senders, separated by comma')
    args = parser.parse_args()
    return args


def load_data(data_paths, filter_conversation=None, filter_sender=None, remove_sender=None, top_n=10):
    # data loading
    df = pd.DataFrame()
    for data_path in data_paths:
        print('Loading', data_path, '...')
        df = pd.concat([df, pd.read_pickle(data_path)])

    df.columns = config.ALL_COLUMNS
    print('Loaded', len(df), 'messages')

    # filtering
    if filter_conversation is not None:
        filter_conversation = filter_conversation.split(',')
        df = df[df['conversationWithName'].isin(filter_conversation)]

    if filter_sender is not None:
        filter_sender = filter_sender.split(',')
        df = df[df['senderName'].isin(filter_sender)]

    if remove_sender is not None:
        remove_sender = remove_sender.split(',')
        df = df[~df['senderName'].isin(remove_sender)]

    # find top_n interlocutors
    mf = df.groupby(['conversationWithName'], as_index=False) \
        .agg(lambda x: len(x)) \
        .sort_values('timestamp', ascending=False)['conversationWithName'] \
        .head(top_n).to_frame()

    print(mf)

    # keep only messages from these top_n interlocutors
    merged = pd.merge(df, mf, on=['conversationWithName'], how='inner')
    merged = merged[['datetime', 'conversationWithName', 'senderName']]

    print('Number to render:', len(merged))
    print(merged.head())
    return merged


def render(data, bin_width, plot_density=False):
    if plot_density:
        # filter out conversationWithName with only one timestamp (which breaks density plot)
        for name in data.conversationWithName.unique():
            if len(data[data.conversationWithName == name].datetime.unique()) == 1:
                data = data[data.conversationWithName != name]

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
    data_check()
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
