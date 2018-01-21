#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import argparse
import sys

import pandas as pd
from ggplot import *

# avoids unicode errors
reload(sys)
sys.setdefaultencoding('utf-8')

# arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument('-d', '-data', dest='dataPaths', nargs='+', help='chat log data files (pickle files)',
                    required=True)
parser.add_argument("-plotDensity", dest='density', action='store_true',
                    help="plots the message densities (KDE) instead of their count")
parser.add_argument("-n", "-numberSenders", dest='topN', type=int, default=10,
                    help="number of different senders to consider, ordered by number of messages sent")
parser.add_argument("-b", "-binWidth", dest='binWidth', type=int, default=25, help="bin width for histograms")
parser.add_argument("-filterConversation", dest='filterConversation', type=str, default=None,
                    help="only keep messages sent in a conversation with this sender")
parser.add_argument("-filterSender", dest='filterSender', type=str, default=None,
                    help="only keep messages sent by this sender")
parser.add_argument("-removeSender", dest='removeSender', type=str, default=None,
                    help="remove messages sent by this sender")
args = parser.parse_args()

dataPaths = args.dataPaths
topN = args.topN
binWidth = args.binWidth
filterConversation = args.filterConversation
filterSender = args.filterSender
removeSender = args.removeSender
plotDensity = args.density

# data loading
df = pd.DataFrame()
for dataPath in dataPaths:
    print 'Loading', dataPath, '...'
    df = pd.concat([df, pd.read_pickle(dataPath)])

df.columns = ['timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text', 'platform', 'language',
              'datetime']
print 'Loaded', len(df), 'messages'

# filtering
if filterConversation is not None:
    df = df[df['conversationWithName'] == filterConversation]

if filterSender is not None:
    df = df[df['senderName'] == filterSender]

if removeSender is not None:
    df = df[df['senderName'] != removeSender]

# keep only topN interlocutors
mf = df.groupby(['conversationWithName'], as_index=False) \
    .agg(lambda x: len(x)) \
    .sort_values('timestamp', ascending=False)['conversationWithName'] \
    .head(topN).to_frame()

print mf

merged = pd.merge(df, mf, on=['conversationWithName'], how='inner')
merged = merged[['datetime', 'conversationWithName', 'senderName']]

print "Number to render:", len(merged)
print merged.head()

# rendering
if plotDensity:
    plot = ggplot(merged, aes(x='datetime', color='conversationWithName')) \
           + geom_density() \
           + scale_x_date(labels='%b %Y') \
           + ggtitle("Conversation Densities") \
           + ylab("Density") \
           + xlab("Date")
else:
    plot = ggplot(merged, aes(x='datetime', fill='conversationWithName')) \
           + geom_histogram(alpha=0.6, binwidth=binWidth) \
           + scale_x_date(labels='%b %Y', breaks='6 months') \
           + ggtitle("Message Breakdown") \
           + ylab("Number of Messages") \
           + xlab("Date")

print plot
