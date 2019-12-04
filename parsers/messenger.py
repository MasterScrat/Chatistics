from parsers.config import config
from parsers.utils import export_dataframe, timestamp_to_ordinal
import argparse
import json
import os
import pandas as pd
import logging

log = logging.getLogger(__name__)


def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    data = []
    # make sure we don't crash if chat logs contain exotic characters
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
                    # TODO handle group chats
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
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'messenger'
    log.info('Detecting languages...')
    df['language'] = 'unknown'
    log.info('Computing dates...')
    df['datetime'] = df['timestamp'].apply(lambda x: x / 1000).apply(timestamp_to_ordinal)
    export_dataframe(df, 'messenger.pkl')
    log.info('Done.')
