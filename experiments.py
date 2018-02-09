import pandas as pd
import numpy as np
from ggplot import *
import sys
from random import randint
import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer

df = pd.DataFrame()
df = pd.concat([df, pd.read_pickle('data/hangouts.pkl')])
df = pd.concat([df, pd.read_pickle('data/messenger.pkl')])

df.columns = ['timestamp', 'conversationWithName', 'senderName', 'text', 'platform', 'language', 'datetime']
print('Loaded', len(df), 'messages')

#df.head()


# RANDOM EXPERIMENTS IN PROGRESS BELOW

# computes average word length
#df3['length'] = df3.apply(lambda x: 0 if x.text==None else len(x.text), axis=1)
#df['nwords'] = df.apply(lambda x: 0 if x.text==None else len(x.text.split()), axis=1)
#df['awlength'] = df.apply(lambda x: 0 if x.text==None else sum(len(word) for word in x.text.split())/(x['nwords']+1.0), axis=1)

# keeps only topN senders
topN = 15
mf = df.groupby(['conversationWithName'], as_index=False) \
        .agg(lambda x:len(x))\
        .sort_values('timestamp', ascending=False)['conversationWithName']\
        .head(topN-1)\
        .to_frame()

df2 = pd.merge(df, mf, on=['conversationWithName'], how='inner')

# augments data
df3['timeOfDay'] = df3['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(float(x)).hour) # ?? only up to 12
df3['dayOfWeek'] = df3['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(float(x)).weekday())

# sentiment analysis!
df3 = df2[df2.text.notnull()].dropna()
df3 = df3[df3.language == 'en']
df3 = df3[df3.text.map(len) > 3]

sid = SentimentIntensityAnalyzer()
df3['sentiment'] = df3['text'].apply(lambda x: sid.polarity_scores(x)['compound'])

print(ggplot(aes(x='sentiment', fill='senderName'), data=df3[df3.conversationWithName == 'Raluca Halalai']) + geom_density(alpha=0.7))
print(ggplot(aes(x='sentiment', fill='senderName'), data=df3[df3.conversationWithName.str.contains('Ana Trisovic')]) + geom_density(alpha=0.7))

# :D
print(ggplot(aes(x='datetime', y='sentiment', color='senderName'), data=df3[df3.conversationWithName.str.contains('Ralu')][df3.sentiment != 0]) + geom_point(alpha=0.05) + scale_x_date(labels='%b %Y')  + stat_smooth(method='loess'))
print(ggplot(df3[df3.text.map(len) < 250], aes(y='dayOfWeek', x='length')) + geom_boxplot())

# compute delta timestamp
df2['timestamp'] = df2['timestamp'].apply(lambda x: int(x))
df2 = df2.sort_values('timestamp', ascending=True)
df2['deltaTimestamp'] = df2.groupby(['conversationWithName', 'senderName'])['timestamp'].apply(lambda x: x - x.shift(1))

# time since previous msg
print(ggplot(aes(x='deltaTimestamp', fill='senderName'), data=df2[df2.deltaTimestamp < 60*30]) + geom_density(alpha=0.7) + xlim(0, 60*5))

# TOO SLOW! deltaTimestamp histogram
#print ggplot(aes(x='deltaTimestamp', fill='conversationWithName'), data=df2.head(50000)) + geom_histogram(alpha=0.7, binwidth=100)

# plots AWL density
print(ggplot(aes(x='awlength', fill='conversationWithName'), data=df2) + geom_density(alpha=0.7) + xlim(0, 10))

# doesnt work?! to check!
#df2 = df[(df['senderName']=='Florian Laurent') | (df['senderName']=='Nicolas Blanc')] 

# language histogram
print(ggplot(aes(x='datetime', fill='language'), data=df) + geom_histogram(alpha=0.7)  + scale_x_date(labels='%b %Y'))

# message length densities
print(ggplot(aes(x='length', fill='senderName'), data=df2) + geom_density(alpha=0.7) + xlim(0, 150))

# histogram of message lengths
print(ggplot(aes(x='length', fill='senderName'), data=df3) + geom_histogram(alpha=0.7, binwidth=binWidth) + ylim(0, 5000) + xlim(0, 150))

# messages containing "kill you"
df[df.text.notnull()][df.text.dropna().str.contains('kill you')][['senderName', 'conversationWithName', 'text']]
df[df.text.str.contains('kill you', na=False)][['senderName', 'conversationWithName', 'text']]

# platform usage histogram
print(ggplot(aes(x='timestamp', fill='platform'), data=df) + geom_histogram(alpha=0.7, binwidth=100) + scale_x_date(labels='%b %Y'))

# MISC
# finding the max
df.col1.str.len().max()
df.col1.map(lambda x: len(x)).max()
df.col1.map(len).max()

# filter base on part of string
df[df['A'].str.contains("hello")]

# keep only rows where text length > 3
df3[df3.text.map(len) > 3]

# if in lambda
# lambda x: True if x % 2 == 0 else False
