import pandas as pd
import os
import sys
from parsers.config import config
import glob
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from visualizers.utils import save_fig
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

log = logging.getLogger(__name__)


def load_data(args):
    # input paths
    if len(args['platforms']) == 0:
        log.info('No platforms specified')
        exit(0)
    df = []
    for platform in args['platforms']:
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
    if len(args['filter_conversation']) > 0:
        df = df[df['conversationWithName'].isin(args['filter_conversation'])]
    if len(args['remove_conversation']) > 0:
        df = df[~df['conversationWithName'].isin(args['remove_conversation'])]
    if len(args['remove_sender']) > 0:
        df = df[~df['senderName'].isin(args['remove_sender'])]

    # find top_n interlocutors
    top_interlocutors = df.conversationWithName.value_counts().iloc[:args['top_n']]
    df = df[df['conversationWithName'].isin(top_interlocutors.index)]
    if len(df) > 0:
        log.info(f'Loaded a total of {len(df):,} messages ({original_len-len(df):,} removed by filters)')
    else:
        log.warning(f'With the given filters no messages could be found!')
        exit(-1)
    return df


def render_barplot(df, **args):
    # create figure
    sns.set()
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    df['timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    df['count'] = 0
    df = df.set_index('timestamp')
    df = df.groupby('conversationWithName').resample('1M').count()['count']
    df = df.unstack(fill_value=0).T
    df = df.reset_index()
    df = df.set_index('timestamp')
    df.plot(kind='bar', stacked=True, ax=ax)
    # Axis labels
    ax.set_xlabel('')
    ax.set_ylabel('Messages per month')
    # Legend
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
    # Make most of the ticklabels empty so the labels don't get too crowded
    ticklabels = ['']*len(df.index)
    # Every 4th ticklable shows the month and day
    ticklabels[::4] = [item.strftime('%b') for item in df.index[::4]]
    # Every 12th ticklabel includes the year
    ticklabels[::12] = [item.strftime('%b %Y') for item in df.index[::12]]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    save_fig(fig, 'breakdown')

def render_density(df, **args):
    sns.set()
    fig, ax = plt.subplots(1, 1, figsize=(20,10))
    df['timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    df['timestamp'] = df.timestamp.apply(lambda s: mdates.date2num(s))
    for name, g in df.groupby('conversationWithName'):
        sns.distplot(g['timestamp'], ax=ax, hist=False, label=name)
    ax.set_ylabel('Density')
    ax.set_xlabel('')
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.tight_layout()
    save_fig(fig, 'density')


def main(**args):
    df = load_data(args)
    if args['as_density']:
        render_density(df, **args)
    else:
        render_barplot(df, **args)
