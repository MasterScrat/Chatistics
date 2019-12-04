from parsers.config import config
from parsers.utils import export_dataframe, timestamp_to_ordinal, detect_language
import argparse
import json
import os
import pandas as pd
import logging

log = logging.getLogger(__name__)

def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    log.info('Parsing Facebook messenger data...')
    if own_name is None:
        own_name = infer_own_name(file_path)
    data = parse_messages(file_path, own_name)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'messenger'
    log.info('Detecting languages...')
    df = detect_language(df)
    log.info('Computing dates...')
    df['datetime'] = df['timestamp'].apply(lambda x: x / 1000).apply(timestamp_to_ordinal)
    export_dataframe(df, 'messenger.pkl')
    log.info('Done.')


def parse_messages(file_path, own_name):
    data = []
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            conversation_id = root.split('/')[-1]
            conversation_with_name = None
            document = os.path.join(root, filename)
            with open(document) as f:
                json_data = json.load(f)
            if "messages" not in json_data or "participants" not in json_data:
                log.warning(f"Missing messages or participant list in conversation {conversation_id}")
                continue
            participants = json_data["participants"]
            if len(participants) < 2:
                log.warning(f"User with id {conversation_id} left Facebook, we don't know what their name was.")
            if len(participants) > 2:
                log.info("Group chats are not supported yet.")
                continue
            for participant in participants:
                if participant['name'] != own_name:
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
                    outgoing = sender_name == own_name
                    data += [[timestamp, conversation_id, conversation_with_name, sender_name, outgoing, content, '', '', '']]
                    if len(data) >= MAX_EXPORTED_MESSAGES:
                        log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                        return data
    return data


def infer_own_name(file_path, min_conversations=2):
    """Infers own name from multiple conversations"""
    conversation_participants = []
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            document_path = os.path.join(root, filename)
            with open(document_path, 'r') as f:
                json_data = json.load(f)
            if "participants" not in json_data:
                continue
            participants = json_data['participants']
            # only consider conversations between two participants
            conversation_participants.append(set([p['name'] for p in participants]))
            if len(conversation_participants) >= min_conversations:
                own_name = set.intersection(*conversation_participants)
                if len(own_name) == 1:
                    own_name = list(own_name)[0]
                    log.info(f'Successfully inferred own-name to be {own_name}')
                    return own_name
    raise Exception('Could not infer own name from existing converstations. Please provide your username manually with the --own-name argument')
