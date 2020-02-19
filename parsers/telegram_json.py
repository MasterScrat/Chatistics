from parsers.config import config
from parsers.utils import export_dataframe, detect_language
from dateutil.parser import parse
import json
import pandas as pd
import logging
from collections import defaultdict
import os

log = logging.getLogger(__name__)


def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    log.info('Parsing Google Hangouts data...')
    if not os.path.isfile(file_path):
        log.error(f'No input file under {file_path}')
        exit(0)
    archive = read_archive(file_path)
    if own_name is None:
        own_name = " ".join([archive["personal_information"]["first_name"], archive["personal_information"]["last_name"]])
    own_id = archive["personal_information"]["user_id"]
    data = parse_messages(archive, own_id)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'telegram'
    log.info('Detecting languages...')
    df = detect_language(df)
    export_dataframe(df, config['telegram_json']['OUTPUT_PICKLE_NAME'])
    log.info('Done.')


def parse_messages(archive, own_id):
    def json_to_text(data):
        result = ""
        for v in data:
            if isinstance(v, dict):
                result += v["text"]
            else:
                result += v
        return result

    data = []
    log.info('Extracting messages...')
    for chat in archive["chats"]["list"]:
        chat_type = chat["type"]
        if chat_type == "personal_chat" or chat_type == "private_group" or chat_type == "private_supergroup":
            conversation_with_id = chat["id"]
            conversation_with_name = chat["name"]
            for message in chat["messages"]:
                if message["type"] != "message":
                    continue
                timestamp = parse(message["date"]).timestamp()
                # skip text from forwarded messages
                text = message["text"] if "forwarded_from" not in message else ""
                if "sticker_emoji" in message:
                    text = message["sticker_emoji"]
                if isinstance(text, list):
                    text = json_to_text(text)
                sender_name = message["from"]
                sender_id = message["from_id"]
                if sender_name is None:
                    # unknown sender
                    log.error(f"No senderName could be found for senderId ({sender_id})")

                # saves the message
                outgoing = sender_id == own_id
                data += [[timestamp, conversation_with_id, conversation_with_name, sender_name, outgoing, text, '', '']]

                if len(data) >= MAX_EXPORTED_MESSAGES:
                    log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                    return data
    return data


def read_archive(file_path):
    log.info(f'Reading archive file {file_path}...')
    with open(file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())
    return archive
