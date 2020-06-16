from parsers.config import config
from parsers.utils import export_dataframe, detect_language
import json
import pandas as pd
import logging
from bs4 import BeautifulSoup
from collections import defaultdict
from dateutil.parser import parse
import os
import html
import warnings

log = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    log.info('Parsing Skype data...')
    if not os.path.isfile(file_path):
        log.error(f'No input file under {file_path}')
        exit(0)
    archive = read_archive(file_path)
    own_id = archive["userId"]
    if own_name is None:
        ind = own_id.rfind(":")
        own_name = own_id[ind+1:]
    data = parse_messages(archive, own_id, own_name)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'skype'
    log.info('Detecting languages...')
    df = detect_language(df)
    export_dataframe(df, config['skype']['OUTPUT_PICKLE_NAME'])
    log.info('Done.')


def parse_messages(archive, own_id, own_name):
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

    names = {}
    data = []
    log.info('Extracting names...')
    for conversation in archive["conversations"]:
        if conversation["threadProperties"]:
            for message in conversation["MessageList"]:
                sender_id = message["from"]
                sender_name = message["displayName"]
                if sender_name:
                    sender_name = html.unescape(sender_name)
                    save_name_for_id(sender_name, sender_id)
        else:
            conversation_with_id = conversation["id"]
            conversation_with_name = conversation["displayName"]
            if conversation_with_name:
                conversation_with_name = html.unescape(conversation_with_name)
                save_name_for_id(conversation_with_name, conversation_with_id)

    save_name_for_id(own_name, own_id)

    log.info('Extracting messages...')
    for conversation in archive["conversations"]:
        conversation_with_id = conversation["id"]
        conversation_with_name = conversation["displayName"]
        if conversation_with_name:
            conversation_with_name = html.unescape(conversation_with_name)
        else:
            # If conversation_with_name is None we are collecting caller log files -> skip
            continue
        for message in conversation["MessageList"]:
            message_type = message["messagetype"]
            timestamp = parse(message["originalarrivaltime"]).timestamp()
            content = message["content"]
            sender_id = message["from"]
            sender_name = message["displayName"]
            if sender_name:
                sender_name = html.unescape(sender_name)
            outgoing = sender_id == own_id

            if message_type == "RichText":
                if not sender_name:
                    sender_name = id_to_name(sender_id)
                if sender_name is None:
                    # unknown sender
                    log.error(f"No senderName could be found for senderId ({sender_id})")
                    ind = sender_id.rfind(":")
                    sender_name = sender_id[ind+1:]
                    save_name_for_id(sender_name, sender_id)

                soup = BeautifulSoup(content, "html.parser")

                # remove quotes
                for script in soup(["quote", "legacyquote"]):
                    script.extract()

                content = soup.get_text()

                # saves the message
                data += [[timestamp, conversation_with_id, conversation_with_name, sender_name, outgoing, content, '', '']]

                if len(data) >= MAX_EXPORTED_MESSAGES:
                    log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                    return data
            elif message_type == "Text":
                if not sender_name:
                    sender_name = id_to_name(sender_id)
                if sender_name is None:
                    # unknown sender
                    log.error(f"No senderName could be found for senderId ({sender_id})")
                    ind = sender_id.rfind(":")
                    sender_name = sender_id[ind+1:]
                    save_name_for_id(sender_name, sender_id)

                # saves the message
                data += [[timestamp, conversation_with_id, conversation_with_name, sender_name, outgoing, content, '', '']]

                if len(data) >= MAX_EXPORTED_MESSAGES:
                    log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                    return data
    return data


def read_archive(file_path):
    log.info(f'Reading archive file {file_path}...')
    with open(file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())
    return archive

