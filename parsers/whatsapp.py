import pandas as pd
from parsers.utils import export_dataframe, detect_language, timestamp_to_ordinal
from parsers.config import config
import logging
import glob
import os
import re
from datetime import datetime
import uuid
from collections import defaultdict

log = logging.getLogger(__name__)
regex_message = re.compile(r'^[^0-9]{0,2}([0-9./\-]+,?[\sT][0-9:]+)[^0-9]?\s[\-]?\s?(([^:]+):)?(.+)?$')


def main(own_name, file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    log.info('Parsing Whatsapp data...')
    files = glob.glob(os.path.join(file_path, '*.txt'))
    if len(files) == 0:
        log.error(f'No input files found under {file_path}')
        exit(0)
    if own_name is None:
        own_name = infer_own_name(files)
    data = parse_messages(files, own_name)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'whatsapp'
    log.info('Detecting languages...')
    df = detect_language(df)
    log.info('Converting dates...')
    df['datetime'] = df['timestamp'].apply(timestamp_to_ordinal)
    # Export
    export_dataframe(df, config['whatsapp']['OUTPUT_PICKLE_NAME'])
    log.info('Done.')


def parse_messages(files, own_name):
    data = []
    for f_path in files:
        text = ""
        log.info(f'Reading {f_path}')
        f_name = os.path.basename(f_path)
        conversation_id = uuid.uuid4().hex
        participants = set()
        conversation_data = []
        with open(f_path, 'r') as f:
            for line in f:
                matches = regex_message.search(line)
                if not matches and text is not None:
                    # We are parsing a multi-line message
                    text += '\n' + line.strip()
                    continue
                elif matches and text != "":
                    # dump previous entry
                    conversation_data += [[timestamp, conversation_id, '', sender_name, outgoing, text, '', '', '']]
                    text = ""
                    if len(data) + len(conversation_data) >= MAX_EXPORTED_MESSAGES:
                        log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                        # dismiss current conversation data
                        return data
                elif not matches and text is None:
                    # we are not parsing a multi-line message and we have no matches
                    continue
                groups = matches.groups()
                if len(groups) != 4:
                    continue
                # get timestamp
                try:
                    timestamp = pd.to_datetime(groups[0], infer_datetime_format=True).timestamp()
                except ValueError:
                    log.error(f'Could not parse datetime {groups[0]}')
                    # workaround for datetime strings that have different localization in chat export
                    timestamp = datetime.now().timestamp()
                # check if sender present
                sender_name = groups[2]
                if sender_name is not None and sender_name != own_name:
                    participants.add(sender_name)
                outgoing = sender_name == own_name
                text = groups[3] or ""
                text = text.strip()
            if text != "" and sender_name is not None:
                # dump last line
                conversation_data += [[timestamp, conversation_id, '', sender_name, outgoing, text, '', '', '']]
        # fill conversation_with
        if len(participants) == 0:
            conversation_with_name = ''
        else:
            conversation_with_name = '-'.join(sorted(list(participants)))
        for i in range(len(conversation_data)):
            conversation_data[i][2] = conversation_with_name
        # add to existing data
        data.extend(conversation_data)
    return data


def infer_own_name(files, min_conversations=2):
    """Infers own name from multiple conversations by finding the person who participated most in the conversations"""
    if len(files) < min_conversations:
        raise Exception(
            f'Cannot infer own-name from less than {min_conversations} conversations. Please provide your username manually with the --own-name argument.')
    participants_conversation_count = defaultdict(int)
    num_conversations = 0
    log.info('Trying to infer own_name from data...')
    for f_path in files:
        participants = set()
        with open(f_path, 'r') as f:
            for line in f:
                matches = regex_message.search(line)
                if not matches or len(matches.groups()) != 3:
                    continue
                participants.add(matches.group(2))
        if len(participants) > 1:
            num_conversations += 1
            for p in participants:
                participants_conversation_count[p] += 1
    if num_conversations >= min_conversations and len(participants_conversation_count.keys()) >= 2:
        own_name = max(participants_conversation_count, key=participants_conversation_count.get)
        log.info(f'Successfully inferred own-name to be {own_name}')
        return own_name
    raise Exception('Could not infer own name from existing converstations. Please provide your username manually with the --own-name argument')
