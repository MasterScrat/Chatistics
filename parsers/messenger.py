#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import locale
import os
import random
import sys
import time

import pandas as pd
# TODO: There's an etree module in the standard library. Run a try-except so that if they don't have the version of lxml we need, we can fall back to that
# Problematically the methods don't correspond one to one so it'll require
# a good amount of refactoring
from lxml import etree

import utils
import config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--own-name',
        dest='own_name',
        type=str,
        help='name of the owner of the chat logs, written as in the logs',
        required=True)
    parser.add_argument(
        '-f',
        '--file-path',
        dest='file_path',
        help='Facebook chat log file (HTML file)',
        default=config.DEFAULT_MESSENGER_RAW_FILE)
    parser.add_argument(
        '--max',
        '--max-exported-messages',
        dest='max_exported_messages',
        type=int,
        default=config.MAX_EXPORTED_MESSAGES,
        help='maximum number of messages to export')
    args = parser.parse_args()
    return args


def sys_checks():
    """
    Ensure that we have the correct locale and version of Python before we start.
    """
    if locale.getpreferredencoding == 'UTF-8':
        pass
    else:
        sys.exit(
            "We've detected an encoding of: {0}. Unfortunately Chatistics only supports UTF-8 currently.".
            format(locale.getpreferredencoding))

    vers = sys.version_info
    if vers < (3, 5):
        sys.exit("Chatistics requires Python3.5 and up.")


def main():
    sys_checks()
    args = parse_arguments()

    fallback_date_parsing = False
    data = []
    warned_name_changes = []
    nb_invalid_sender = 0

    # make sure we don't crash if chat logs contain exotic characters
    etree.set_default_parser(
        etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))

    for filename in os.listdir(args.file_path):

        if not filename.endswith('.html'):
            continue

        document = os.path.join(args.file_path, filename)
        archive = etree.parse(document)

        conversation_id = filename.replace('.html', '')
        group_conversation = False
        timestamp = ''
        sender_name = ''
        conversation_with_name = None

        for element in archive.iter():
            tag = element.tag
            class_name = element.get('class')
            content = element.text

            if tag == 'p':
                text = content

                if conversation_with_name != '' and sender_name != '':

                    # handles when the interlocutor's name changed at some point
                    if (sender_name != conversation_with_name) and (sender_name != args.own_name) and \
                            (sender_name not in warned_name_changes) and (not group_conversation):
                        if sender_name not in warned_name_changes:
                            print('\t', 'Assuming', sender_name, 'is',
                                  conversation_with_name)
                            warned_name_changes.append(sender_name)

                        sender_name = conversation_with_name

                    data += [[
                        timestamp, conversation_id, conversation_with_name,
                        sender_name, text
                    ]]

                else:
                    nb_invalid_sender = nb_invalid_sender + 1

            elif tag == 'span':
                if class_name == 'user':
                    sender_name = content
                elif class_name == 'meta':
                    try:
                        if not fallback_date_parsing:
                            timestamp = time.mktime(
                                pd.to_datetime(
                                    content,
                                    format='%A, %B %d, %Y at %H:%M%p',
                                    exact=False).timetuple())
                        else:
                            timestamp = time.mktime(
                                pd.to_datetime(
                                    content,
                                    infer_datetime_format=True).timetuple())

                    except ValueError:
                        if not fallback_date_parsing:
                            print(
                                'Unexpected date format. '
                                'Falling back to infer_datetime_format, parsing will be slower.'
                            )
                            timestamp = time.mktime(
                                pd.to_datetime(
                                    content,
                                    infer_datetime_format=True).timetuple())
                            fallback_date_parsing = True
                        else:
                            raise

            elif tag == 'div' and class_name == 'thread':
                nbParticipants = str(element.xpath("text()")).count(', ') + 1
                if nbParticipants > 1:
                    group_conversation = True

            elif tag == 'h3':
                if conversation_with_name is not None:
                    print(
                        'Something is wrong. File format changed? (multiple conversation hearder in a single file)'
                    )
                    exit(0)
                else:
                    content = content.replace('Conversation with ', '')
                    conversation_with_name = content

                print(conversation_id, conversation_with_name, "(group?",
                      group_conversation, ")")

            if len(data) >= args.max_exported_messages:
                break

    print(len(data), 'messages parsed.')

    if nb_invalid_sender > 0:
        print(nb_invalid_sender, 'messages discarded because of bad ID.')

    if len(data) < 1:
        print('Nothing to save.')
        exit(0)

    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
    df['platform'] = 'messenger'

    log.info('Detecting languages...')
    df['language'] = 'unknown'
    for name, group in df.groupby(df.conversationWithName):
        sample = ''
        df2 = df[df.conversationWithName == name].dropna()

        if len(df2) > 10:
            for x in range(0, min(len(df2), 100)):
                sample = sample + df2.iloc[random.randint(
                    0,
                    len(df2) - 1)]['text']

            print('\t', name, detect(sample), "(", len(df2), "msgs)")
            df.loc[df.conversationWithName == name, 'language'] = detect(
                sample)

    log.info('Computing dates...')
    df['datetime'] = df['timestamp'].apply(utils.timestamp_to_ordinal)

    print(df.head())
    utils.export_dataframe(df, 'messenger.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()
