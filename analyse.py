#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
from ggplot import *
from matplotlib import pyplot as plt
import sys

filterConversation = None
plotDensity = False

TOP_N = 10;

# avoids unicode errors
reload(sys)
sys.setdefaultencoding('utf-8')

df1 = pd.read_pickle('data/hangouts.pkl')
df2 = pd.read_pickle('data/messenger.pkl')
df = pd.concat([df1])

df.columns = ['timestamp', 'conversationWithId', 'conversationWithName','senderId', 'senderName', 'text']

# keeps only TOP_N interlocutors
mf = df.groupby(['conversationWithName'], as_index=False) \
        .agg(lambda x:len(x))\
        .sort_values('timestamp', ascending=False)['conversationWithName']\
        .head(TOP_N - 1)\
        .to_frame()

merged = pd.merge(df, mf, on=['conversationWithName'], how='inner')
merged = merged[['timestamp', 'conversationWithName', 'senderName']]

if filterConversation != None:
    merged = merged[merged['conversationWithName'] == filterConversation]

merged = merged[merged['senderName'] != 'Florian Laurent']
merged = merged[merged['senderName'] != 'florian.laurent@gmail.com']

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
    + geom_histogram(alpha=0.6, binwidth=20) \
    + scale_x_date(labels='%b %Y', breaks='3 months') \
    + ggtitle("Message Breakdown") \
    + ylab("Number of Messages")\
    + xlab("Date")
    #+ labs(color = "Interlocutor")

print plot