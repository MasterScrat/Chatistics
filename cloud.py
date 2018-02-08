#!/usr/bin/env python3
import os
import re
import time
import json
import argparse

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud, ImageColorGenerator
from scipy.misc import imread


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', dest='data_paths', nargs='+',
                        help='chat log data files (pickle files)', required=True)
    parser.add_argument('--sw', '--stopwords-paths', dest='stopwords_paths', nargs='+',
                        help='stopword files (JSON format)', default=['stopwords/en.json'])
    parser.add_argument('-m', '--mask-image', dest='mask_image', type=str, default=None,
                        help='image to use as mask', required=True)
    parser.add_argument('--filter-conversation', dest='filter_conversation', type=str, default=None,
                        help='only keep messages sent in a conversation with this sender')
    parser.add_argument('--filter-sender', dest='filter_sender', type=str, default=None,
                        help='only keep messages sent by this sender')
    parser.add_argument('--remove-sender', dest='remove_sender', type=str, default=None,
                        help='remove messages sent by this sender')
    parser.add_argument('-n', '--num-words', dest='num_words', type=int, default=10000, help='bin width for histograms')
    parser.add_argument('--density', '--dpi', dest='density', type=int, default=100, help='rendered image DPI')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    num_words = args.num_words
    density = args.density
    mask_img = args.mask_image

    data_paths = args.data_paths
    stopwords_paths = args.stopwords_paths
    filter_conversation = args.filter_conversation
    filter_sender = args.filter_sender
    remove_sender = args.remove_sender

    print('Mask image:', mask_img)
    print('Up to', num_words, 'words on the cloud')
    print('Image dpi:', density)

    # TODO factor w histo logic
    df = pd.DataFrame()
    for dataPath in data_paths:
        print('Loading messages from %s...' % dataPath)
        df = pd.concat([df, pd.read_pickle(dataPath)])

    df.columns = ['timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text', 'platform', 'language',
                  'datetime']
    print('Loaded', len(df), 'messages')

    if filter_conversation is not None:
        print('Keeping only messages in conversations with', filter_conversation)
        df = df[df['conversationWithName'] == filter_conversation]

    if filter_sender is not None:
        print('Keeping only messages sent by', filter_sender)
        df = df[df['senderName'] == filter_sender]

    if remove_sender is not None:
        print('Removing messages sent by', remove_sender)
        df = df[df['senderName'] != remove_sender]

    if len(df['text']) == 0:
        print('No messages left! review your filter options')
        exit(0)

    print('Final corpus:', len(df['text'])/1000, 'K messages')

    stopwords = []
    for stopwordsPath in stopwords_paths:
        print('Loading stopwords from', stopwordsPath, '...')
        stopwords = stopwords + json.load(open(stopwordsPath))

    stopwords = set(stopwords)
    print('Stopwords:', len(stopwords), 'words')

    # pre-compiled regex is faster than going through a list
    stopwords = '|'.join(stopwords)
    regex = re.compile(r'\b('+stopwords+r')\b', re.UNICODE)

    print('Cleaning up...')
    text = df['text'] \
        .replace(to_replace='None', value=np.nan).dropna() \
        .str.lower() \
        .apply(lambda w: re.sub(r'^https?:\/\/.*[\r\n]*', '', w)) \
        .apply(lambda w: regex.sub('', w))

    text = ' '.join(text)

    print('Rendering...')
    directory = os.path.dirname(__file__)
    mask = imread(os.path.join(directory, mask_img))

    # https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud
    wc = WordCloud(background_color="white", mask=mask,
                   max_words=num_words, stopwords=None, normalize_plurals=False, collocations=True).generate(text)

    image_colors = ImageColorGenerator(mask)
    wc = wc.recolor(color_func=image_colors)

    plt.imshow(wc)
    plt.axis("off")

    path = 'renders/' + str(int(time.time()*1000)) + '.png'
    print('Saving to %s...' % path)
    plt.savefig(path, dpi=density)


if __name__ == '__main__':
    main()
