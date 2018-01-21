#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from os import path
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud, ImageColorGenerator
from scipy.misc import imread
import json
import re
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-d','-data', dest='dataPaths', nargs='+', help='chat log data files (pickle files)', required=True)
parser.add_argument('-sw','-stopwordsPaths', dest='stopwordsPaths', nargs='+', help='stopword files (JSON format)', default=["stopwords/en.json"])
parser.add_argument('-m', '-maskImage', dest='maskImage', type=str, default=None, help="image to use as mask", required=True)
parser.add_argument("-filterConversation", dest='filterConversation', type=str, default=None, help="only keep messages sent in a conversation with this sender")
parser.add_argument("-filterSender", dest='filterSender', type=str, default=None, help="only keep messages sent by this sender")
parser.add_argument("-removeSender", dest='removeSender', type=str, default=None, help="remove messages sent by this sender")
parser.add_argument("-n", "-numWords", dest='numWords', type=int, default=10000, help="bin width for histograms")
parser.add_argument("-density", "-dpi", dest='density', type=int, default=100, help="rendered image DPI")
args = parser.parse_args()

numWords = args.numWords
density = args.density
maskImg = args.maskImage

dataPaths = args.dataPaths
stopwordsPaths = args.stopwordsPaths
filterConversation = args.filterConversation
filterSender = args.filterSender
removeSender = args.removeSender

print 'Mask image:', maskImg
print 'Up to', numWords, 'words on the cloud'
print 'Image dpi:', density

# TODO factor w histo logic
df = pd.DataFrame()
for dataPath in dataPaths:
    print 'Loading messages from', dataPath, '...'
    df = pd.concat([df, pd.read_pickle(dataPath)])

df.columns = ['timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text', 'platform', 'language', 'datetime']
print 'Loaded', len(df), 'messages'

if filterConversation is not None:
    print 'Keeping only messages in conversations with', filterConversation
    df = df[df['conversationWithName'] == filterConversation]

if filterSender is not None:
    print 'Keeping only messages sent by', filterSender
    df = df[df['senderName'] == filterSender]

if removeSender is not None:
    print 'Removing messages sent by', removeSender
    df = df[df['senderName'] != removeSender]

if len(df['text'])==0:
    print 'No messages left! review your filter options'
    exit(0)

print 'Final corpus:', len(df['text'])/1000, 'K messages'

stopwords = []
for stopwordsPath in stopwordsPaths:
    print 'Loading stopwords from', stopwordsPath, '...'
    stopwords = stopwords + json.load(open(stopwordsPath))

stopwords = set(stopwords)
print 'Stopwords:', len(stopwords), 'words'

# pre-compiled regex is faster than going through a list
stopwords = '|'.join(stopwords)
regex = re.compile(r'\b('+stopwords+r')\b', re.UNICODE)

print 'Cleaning up...'
text = df['text'] \
    .replace(to_replace='None', value=np.nan).dropna() \
    .str.lower() \
    .apply(lambda w: re.sub(r'^https?:\/\/.*[\r\n]*', '', w)) \
    .apply(lambda w: regex.sub('', w))

text  = ' '.join(text)

print 'Rendering...'
d = path.dirname(__file__)
mask = imread(path.join(d, maskImg))

# https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud
wc = WordCloud(background_color="white", mask=mask, max_words=numWords, stopwords=None, normalize_plurals=False, collocations=True).generate(text)

image_colors = ImageColorGenerator(mask)
wc = wc.recolor(color_func=image_colors)

plt.imshow(wc)
plt.axis("off")

path = 'renders/' + str(int(time.time()*1000)) + '.png'
print 'Saving to', path, '...'
plt.savefig(path, dpi = density)