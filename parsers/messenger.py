#!/usr/bin/env python3
import os
import time
import random
import argparse
import datetime

import pandas as pd
from langdetect import *
from lxml import etree

from parsers import utils, config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--own-name', dest='own_name', type=str,
                        help='name of the owner of the chat logs, written as in the logs', required=True)
    parser.add_argument('-f', '--file-path', dest='file_path', help='Facebook chat log file (HTML file)',
                        default=config.DEFAULT_MESSENGER_RAW_FILE)
    parser.add_argument('--max', '--max-exported-messages', dest='max_exported_messages', type=int,
                        default=config.MAX_EXPORTED_MESSAGES, help='maximum number of messages to export')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    fallbackDateParsing = False
    data = []
    warnedNameChanges = []
    nbInvalidSender = 0

    # make sure we don't crash if chat logs contain exotic characters
    etree.set_default_parser(etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))

    for filename in os.listdir(args.file_path):

        if not filename.endswith('.html'):
            continue

        document = os.path.join(args.file_path, filename)
        archive = etree.parse(document)

        conversationId = filename.replace('.html', '')
        groupConversation = False
        timestamp = ''
        senderName = ''
        conversationWithName = None

        for element in archive.iter():
            tag = element.tag
            className = element.get('class')
            content = element.text

            if tag == 'p':
                text = content

                if conversationWithName != '' and senderName != '':

                    # handles when the interlocutor's name changed at some point
                    if (senderName != conversationWithName) and (senderName != args.own_name) and \
                            (senderName not in warnedNameChanges) and (not groupConversation):
                        if senderName not in warnedNameChanges:
                            print('\t', 'Assuming', senderName, 'is', conversationWithName)
                            warnedNameChanges.append(senderName)

                        senderName = conversationWithName

                    data += [[timestamp, conversationId, conversationWithName, senderName, text]]

                else:
                    nbInvalidSender = nbInvalidSender + 1

            elif tag == 'span':
                if className == 'user':
                    senderName = content
                elif className == 'meta':
                    try:
                        if not fallbackDateParsing:
                            timestamp = time.mktime(
                                pd.to_datetime(content, format='%A, %B %d, %Y at %H:%M%p', exact=False).timetuple())
                        else:
                            timestamp = time.mktime(pd.to_datetime(content, infer_datetime_format=True).timetuple())

                    except ValueError:
                        if not fallbackDateParsing:
                            print('Unexpected date format. '
                                  'Falling back to infer_datetime_format, parsing will be slower.')
                            timestamp = time.mktime(
                                pd.to_datetime(content, format='%A, %B %d, %Y at %H:%M%p', exact=False).timetuple())
                            fallbackDateParsing = True
                        else:
                            raise

            elif tag == 'div' and className == 'thread':
                nbParticipants = str(element.xpath("text()")).count(', ') + 1
                if nbParticipants > 1:
                    groupConversation = True

            elif tag == 'h3':
                if conversationWithName is not None:
                    print('Something is wrong. File format changed? (multiple conversation hearder in a single file)')
                    exit(0)
                else:
                    content = content.replace('Conversation with ', '')
                    conversationWithName = content

                print(conversationId, conversationWithName, "(group?", groupConversation, ")")

            if len(data) >= args.max_exported_messages:
                break

    print(len(data), 'messages parsed.')

    if nbInvalidSender > 0:
        print(nbInvalidSender, 'messages discarded because of bad ID.')

    if len(data) < 1:
        print('Nothing to save.')
        exit(0)

    print('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
    df['platform'] = 'messenger'

    print('Detecting languages...')
    df['language'] = 'unknown'
    for name, group in df.groupby(df.conversationWithName):
        sample = ''
        df2 = df[df.conversationWithName == name].dropna()

        if len(df2) > 10:
            for x in range(0, min(len(df2), 100)):
                sample = sample + df2.iloc[random.randint(0, len(df2) - 1)]['text']

            print('\t', name, detect(sample), "(", len(df2), "msgs)")
            df.loc[df.conversationWithName == name, 'language'] = detect(sample)

    print('Computing dates...')
    ordinate = lambda x: datetime.datetime.fromtimestamp(float(x)).toordinal()
    df['datetime'] = df['timestamp'].apply(ordinate)

    print(df.head())
    utils.export_dataframe(df, 'messenger.pkl')
    print('Done.')


if __name__ == '__main__':
    main()
