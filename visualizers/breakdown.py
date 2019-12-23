import pandas as pd
import os
import sys
import glob
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from visualizers.utils import save_fig
from utils import load_data
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

log = logging.getLogger(__name__)


def render_barplot(df, args):
    # create figure
    sns.set()
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    df['timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    df['count'] = 0
    df = df.set_index('timestamp')
    df = df.groupby('conversationWithName').resample(args.bin_size).count()['count']
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
    ticklabels = [''] * len(df.index)
    # Every 4th ticklable shows the month and day
    ticklabels[::4] = [item.strftime('%b') for item in df.index[::4]]
    # Every 12th ticklabel includes the year
    ticklabels[::12] = [item.strftime('%b %Y') for item in df.index[::12]]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    save_fig(fig, 'breakdown')


def render_density(df, args):
    sns.set()
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    df['timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    df['timestamp'] = df.timestamp.apply(lambda s: mdates.date2num(s))
    for name, g in df.groupby('conversationWithName'):
        sns.distplot(g['timestamp'], ax=ax, hist=False, label=name, kde_kws={"shade": True})
    ax.set_ylabel('Density')
    ax.set_xlabel('')
    ax.legend(loc='center left', bbox_to_anchor=(1, .5))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.tight_layout()
    save_fig(fig, 'density')


def main(args):
    df = load_data(args)
    if args.as_density:
        render_density(df, args)
    else:
        render_barplot(df, args)
