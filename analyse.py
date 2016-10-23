#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
from ggplot import *
from matplotlib import pyplot as plt
import sys
import argparse

# avoids unicode errors
reload(sys)
sys.setdefaultencoding('utf-8')

# arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument('-d','-data', dest='dataPaths', nargs='+', help='chat log data files (pickle files)', required=True)
parser.add_argument("-plotDensity", dest='density', action='store_true', help="plots the message densities (KDE) instead of their count")
parser.add_argument("-n", "-numberSenders", dest='topN', type=int, default=10, help="number of different senders to consider, ordered by number of messages sent")
parser.add_argument("-b", "-binWidth", dest='binWidth', type=int, default=25, help="bin width for histograms")
parser.add_argument("-filterConversation", dest='filterConversation', type=str, default=None, help="only keep messages sent in a conversation with this sender")
parser.add_argument("-filterSender", dest='filterSender', type=str, default=None, help="only keep messages sent by this sender")
parser.add_argument("-removeSender", dest='removeSender', type=str, default=None, help="remove messages sent by this sender")
args = parser.parse_args()

dataPaths = args.dataPaths
topN = args.topN;
binWidth = args.binWidth
filterConversation = args.filterConversation
filterSender = args.filterSender
plotDensity = args.density
removeSender = args.removeSender

# data loading
df = pd.DataFrame()
for dataPath in dataPaths:
    print 'Loading', dataPath
    df = pd.concat([df, pd.read_pickle(dataPath)])

df.columns = ['timestamp', 'conversationWithName', 'senderName', 'text']

# filtering
if filterConversation != None:
    df = df[df['conversationWithName'] == filterConversation]

if filterSender != None:
    df = df[df['senderName'] == filterSender]

if removeSender != None:
    df = df[df['senderName'] != removeSender]

# keep only topN interlocutors
mf = df.groupby(['conversationWithName'], as_index=False) \
        .agg(lambda x:len(x))\
        .sort_values('timestamp', ascending=False)['conversationWithName']\
        .head(topN-1)\
        .to_frame()

merged = pd.merge(df, mf, on=['conversationWithName'], how='inner')
merged = merged[['timestamp', 'conversationWithName', 'senderName']]

# rendering
if plotDensity == True:
    plot = ggplot(aes(x='timestamp', color='conversationWithName', fill='conversationWithName'), data=merged) \
    + geom_density(alpha=0.6) \
    + scale_x_date(labels='%b %Y') \
    + ggtitle("Conversation Densities") \
    + ylab("Density")\
    + xlab("Date")
    #+ labs(color = "Interlocutor")
else:
    plot = ggplot(aes(x='timestamp', color='senderName', fill='senderName'), data=merged) \
    + geom_histogram(alpha=0.6, binwidth=binWidth) \
    + scale_x_date(labels='%b %Y', breaks='6 months') \
    + ggtitle("Message Breakdown") \
    + ylab("Number of Messages")\
    + xlab("Date")
    #+ labs(color = "Sender Name")

print plot