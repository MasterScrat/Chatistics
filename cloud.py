#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from os import path
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud, ImageColorGenerator
from scipy.misc import imread
import json
import re

NUM_WORDS = 10000
DENSITY = 100
NAME_SENDER = 'Timoklia Kousi'
MASK_IMG = 'img/tim.jpg'

print 'Drawing messages from:', NAME_SENDER, 'mask:', MASK_IMG
print NUM_WORDS, 'words, resolution:', DENSITY/100.0,'x'

df1 = pd.read_pickle('data/hangouts.pkl')
df2 = pd.read_pickle('data/messenger.pkl')
df = pd.concat([df1, df2])
df.columns = ['timestamp', 'conversationWithName', 'senderName', 'text']

df = df[df['senderName'] == NAME_SENDER]

print 'Corpus:', len(df['text'])/1000, 'K messages'

# https://github.com/6/stopwords-json
fr = json.load(open('stopwords/fr.json'))
en = json.load(open('stopwords/en.json'))

stopwords = set(en+fr)
print 'Stopwords:', len(stopwords), 'words'

stopwords = '|'.join(stopwords)
regex = re.compile(r'\b('+stopwords+r')\b', re.UNICODE)

print 'Cleaning up...'
text = []
for msg in df['text']:
    if msg != None:
        msg = msg.lower()
        msg = re.sub(r'^https?:\/\/.*[\r\n]*', '', msg)
        msg = regex.sub('', msg)
        text.append(msg)

text = ' '.join(text)

print 'Rendering...'
d = path.dirname(__file__)
mask = imread(path.join(d, MASK_IMG))

# https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud
wc = WordCloud(background_color="white", mask=mask, max_words=NUM_WORDS, stopwords=None).generate(text)

image_colors = ImageColorGenerator(mask)
wc = wc.recolor(color_func=image_colors)

plt.imshow(wc)
plt.axis("off")

print 'Saving...'
plt.savefig('renders/' + NAME_SENDER.replace(' ', '_') + '_' + str(NUM_WORDS) + '_' + str(DENSITY) + '.png', dpi = DENSITY)

#plt.show()

#export LC_ALL=en_US.UTF-8
#export LANG=en_US.UTF-8