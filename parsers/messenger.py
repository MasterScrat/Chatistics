#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import config
import json
import locale
import os
import pandas as pd
import utils

from parsers import log
from parsers import utils, config


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
    if locale.getpreferredencoding() == 'UTF-8':
        pass
    else:
        sys.exit("We've detected an encoding of: {0}. Unfortunately Chatistics only supports UTF-8 currently.".format(locale.getpreferredencoding()))

    vers = sys.version_info
    if vers < (3, 5):
        sys.exit("Chatistics requires Python3.5 and up.")


def main():
    sys_checks()
    args = parse_arguments()

    fallbackDateParsing = False
    data = []
    warnedNameChanges = []
    nbInvalidSender = 0

    # make sure we don't crash if chat logs contain exotic characters
    for root, dirs, files in os.walk(args.file_path):
        for filename in files:
            if not filename.endswith('.json'):
                continue

            document = os.path.join(root, filename)
            with open(document) as f:
                json_data = json.load(f)

                if "messages" not in json_data or "participants" not in json_data:
                    print("Missing messages or participants.")
                    continue

                if len(json_data["participants"]) > 2:
                    # Ignore group chats
                    # print("Group chat :-(")
                    continue

                for message in json_data["messages"]:
                    timestamp = message["timestamp_ms"]
                    if "content" in message and "sender_name" in message:
                        content = message["content"]
                        sender_name = message["sender_name"]
                        if sender_name != args.own_name:
                            data += [[timestamp, sender_name, sender_name, sender_name, content]]

    print(len(data), 'messages parsed.')

    if nbInvalidSender > 0:
        print(nbInvalidSender, 'messages discarded because of bad ID.')

    if len(data) < 1:
        print('Nothing to save.')
        exit(0)

    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
    df['platform'] = 'messenger'

    log.info('Detecting languages...')
    df['language'] = 'unknown'

    log.info('Computing dates...')
    df['datetime'] = df['timestamp'].apply(lambda x: x/1000).apply(utils.timestamp_to_ordinal)

    print(df.head())
    utils.export_dataframe(df, 'messenger.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()
