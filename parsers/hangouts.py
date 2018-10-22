#!/usr/bin/env python3
import json
import pandas as pd
import argparse
from random import randint
from langdetect import *

from __init__ import log
from . import utils
from config import *


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--own-name', dest='own_name', type=str,
                        help='name of the owner of the chat logs, written as in the logs', required=True)
    parser.add_argument('-f', '--file-path', dest='file_path', help='Hangouts chat log file',
                        default=DEFAULT_HANGOUTS_RAW_FILE)
    parser.add_argument('--max', '--max-exported-messages', dest='max_exported_messages', type=int,
                        default=MAX_EXPORTED_MESSAGES, help='maximum number of messages to export')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    own_name = args.own_name

    print('Parsing JSON file...')
    with open(args.file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())

    names = {}

    def id_to_name(id):
        if id in names:
            return names[id]
        else:
            return None

    def save_name_for_id(name, id):
        if not id in names:
            names[id] = name
        elif names[id] != name:
            print('Assuming', name, 'is', names[id])

    data = []
    conversation_with_id = ''
    conversationWithName = ''

    print('Extracting messages...')
    for conversation in archive["conversations"]:
        if "conversation" in conversation["conversation"]:
            for participant in conversation["conversation"]["conversation"]["participant_data"]:
                if "fallback_name" in participant:
                    save_name_for_id(participant["fallback_name"], participant["id"]["gaia_id"])

        for event in conversation["events"]:
            timestamp = int(event["timestamp"])

            if "chat_message" in event and "segment" in event["chat_message"]["message_content"]:
                content = event["chat_message"]["message_content"]
                text = content["segment"][0]["text"]
                conversationId = event["conversation_id"]["id"]
                sender_id = event["sender_id"]["chat_id"]

                participants = conversation["conversation"]["conversation"]["current_participant"]

                if len(participants) == 2:
                    for participant in participants:
                        if id_to_name(participant["gaia_id"]) != own_name:
                            conversation_with_id = participant["gaia_id"]

                    if id_to_name(sender_id) is not None or id_to_name(conversation_with_id) is not None:
                        if id_to_name(sender_id) != own_name and sender_id != conversation_with_id:
                            # print idToName(senderId), 'in conversation with', idToName(conversationWithId), '!'
                            print('Parsing error, is your ownId correct?')
                            exit(0)

                        # saves the message
                        timestamp = timestamp / 1000000
                        data += [[timestamp, conversationId, id_to_name(conversation_with_id), id_to_name(sender_id), text]]

                    else:
                        # unknown sender
                        print("No senderName for either senderId", sender_id, conversation_with_id)

                    if len(data) >= args.max_exported_messages:
                        break

    log.debug('{} messages parsed.'.format(len(data)))

    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = DATAFRAME_COLUMNS
    df['platform'] = 'hangouts'

    log.info('Detecting languages...')
    df['language'] = 'unknown'
    for name, group in df.groupby(df.conversationWithName):
        sample = ''
        df2 = df[df.conversationWithName == name].dropna()

        if len(df2) > 10:
            for x in range(0, min(len(df2), 100)):
                sample = sample + df2.iloc[randint(0, len(df2) - 1)]['text']

            print('\t', name, detect(sample))
            df.loc[df.conversationWithName == name, 'language'] = detect(sample)

    log.info('Computing dates...')
    df['datetime'] = df['timestamp'].apply(utils.timestamp_to_ordinal)

    print(df.head())
    utils.export_dataframe(df, 'hangouts.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()
