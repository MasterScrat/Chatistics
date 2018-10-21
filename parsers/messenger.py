#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os

import config
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


def main():
    args = parse_arguments()

    data = []

    # make sure we don't crash if chat logs contain exotic characters
    for root, dirs, files in os.walk(args.file_path):
        for filename in files:
            if not filename.endswith('.json'):
                continue

            conversation_id = root.split('/')[-1]
            conversation_with_name = None

            document = os.path.join(root, filename)
            with open(document) as f:
                json_data = json.load(f)

                if "messages" not in json_data or "participants" not in json_data:
                    print("Missing messages or participant list in conversation {}".format(conversation_id))
                    continue

                participants = json_data["participants"]

                if len(participants) < 2:
                    print("User with id {} left Facebook, we don't know what their name was.".format(conversation_id))

                if len(participants) > 2:
                    # TODO handle group chats
                    continue

                for participant in participants:
                    if participant['name'] != args.own_name:
                        conversation_with_name = participant['name']

                if conversation_with_name is None: conversation_with_name = conversation_id

                for message in json_data["messages"]:
                    timestamp = message["timestamp_ms"]
                    if "content" in message and "sender_name" in message:
                        content = message["content"]

                        if "sender_name" in message:
                            sender_name = message["sender_name"]
                        else:
                            sender_name = conversation_id

                        data += [[timestamp, conversation_id, conversation_with_name, sender_name, content]]

    print(len(data), 'messages parsed.')

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
    df['datetime'] = df['timestamp'].apply(lambda x: x / 1000).apply(utils.timestamp_to_ordinal)

    print(df.head())
    utils.export_dataframe(df, 'messenger.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()
