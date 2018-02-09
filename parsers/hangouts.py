#!/usr/bin/env python3
import json
import pandas as pd
import argparse
from random import randint
from langdetect import *

from parsers import log
from parsers import utils, config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--own-name', dest='own_name', type=str,
                        help='name of the owner of the chat logs, written as in the logs', required=True)
    parser.add_argument('-f', '--file-path', dest='file_path', help='Hangouts chat log file',
                        default=config.DEFAULT_HANGOUTS_RAW_FILE)
    parser.add_argument('--max', '--max-exported-messages', dest='max_exported_messages', type=int,
                        default=config.MAX_EXPORTED_MESSAGES, help='maximum number of messages to export')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    own_name = args.own_name

    print('Parsing JSON file...')
    with open(args.file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())

    names = {}

    def idToName(id):
        if id in names:
            return names[id]
        else:
            return None

    def saveNameForId(name, id):
        if not id in names:
            names[id] = name
        elif names[id] != name:
            print('Assuming', name, 'is', names[id])

    data = []
    conversationWithId = ''
    conversationWithName = ''

    print('Extracting messages...')
    for state in archive["conversation_state"]:
        if "conversation" in state["conversation_state"]:
            for participant in state["conversation_state"]["conversation"]["participant_data"]:
                if "fallback_name" in participant:
                    saveNameForId(participant["fallback_name"], participant["id"]["gaia_id"])

        for event in state["conversation_state"]["event"]:
            timestamp = int(event["timestamp"])

            if "chat_message" in event and "segment" in event["chat_message"]["message_content"]:
                content = event["chat_message"]["message_content"]
                text = content["segment"][0]["text"]
                conversationId = event["conversation_id"]["id"]
                senderId = event["sender_id"]["chat_id"]

                participants = state["conversation_state"]["conversation"]["current_participant"]

                if len(participants) == 2:
                    for participant in participants:
                        if idToName(participant["gaia_id"]) != own_name:
                            conversationWithId = participant["gaia_id"]

                    if idToName(senderId) is not None or idToName(conversationWithId) is not None:
                        if idToName(senderId) != own_name and senderId != conversationWithId:
                            # print idToName(senderId), 'in conversation with', idToName(conversationWithId), '!'
                            print('Parsing error, is your ownId correct?')
                            exit(0)

                        # saves the message
                        timestamp = timestamp / 1000000
                        data += [[timestamp, conversationId, idToName(conversationWithId), idToName(senderId), text]]

                    else:
                        # unknown sender
                        print("No senderName for either senderId", senderId, conversationWithId)

                    if len(data) >= args.max_exported_messages:
                        break

    log.debug('{} messages parsed.'.format(len(data)))

    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
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
