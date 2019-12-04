from parsers.config import config
from parsers.utils import export_dataframe, timestamp_to_ordinal
import json
import pandas as pd
import argparse
from random import randint
from langdetect import *
import logging

log = logging.getLogger(__name__)


def read_archive(file_path):
    log.info(f'Reading archive file {file_path}...')
    with open(file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())
    return archive


def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages

    names = {}
    archive = read_archive(file_path)

    def id_to_name(_id):
        if _id in names:
            return names[_id]
        else:
            return None

    def save_name_for_id(name, _id):
        if not _id in names:
            names[_id] = name
        elif names[_id] != name:
            log.info(f'Assuming {name} is {names[_id]}')

    data = []
    log.info('Extracting messages...')
    for conversation in archive["conversations"]:
        conversation_with_id = ''
        conversationWithName = ''
        if "conversation" in conversation["conversation"]:
            for participant in conversation["conversation"]["conversation"]["participant_data"]:
                if "fallback_name" in participant:
                    save_name_for_id(participant["fallback_name"], participant["id"]["chat_id"])
        for event in conversation["events"]:
            if "chat_message" in event and "segment" in event["chat_message"]["message_content"]:
                timestamp = int(event["timestamp"])
                content = event["chat_message"]["message_content"]
                text = content["segment"][0]["text"]
                conversationId = event["conversation_id"]["id"]
                sender_id = event["sender_id"]["chat_id"]
                participants = conversation["conversation"]["conversation"]["current_participant"]
                if len(participants) == 2:
                    for participant in participants:
                        if id_to_name(participant["chat_id"]) != own_name:
                            conversation_with_id = participant["chat_id"]
                    sender_name = id_to_name(sender_id)
                    conversation_with_name = id_to_name(conversation_with_id)
                    if sender_name is not None or conversation_with_name is not None:
                        if sender_name != own_name and sender_id != conversation_with_id:
                            log.error(f'Parsing error. Is your own_name {own_name} correct?')
                            exit(0)
                        # saves the message
                        timestamp = timestamp / 1000000
                        outgoing = sender_name == own_name
                        data += [[timestamp, conversationId, conversation_with_name, sender_name, outgoing, text, '', '', '']]
                    else:
                        # unknown sender
                        log.error(f"No senderName could be found for either senderId ({sender_id}) or ConversationWithId ({conversation_with_id})")
                    if len(data) >= MAX_EXPORTED_MESSAGES:
                        break
    log.info('{:,} messages parsed.'.format(len(data)))
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
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
    log.info('Converting dates...')
    df['datetime'] = df['timestamp'].apply(timestamp_to_ordinal)

    # Export
    export_dataframe(df, 'hangouts.pkl')
    log.info('Done.')
