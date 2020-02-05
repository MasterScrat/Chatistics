from parsers.config import config
from parsers.utils import export_dataframe, detect_language
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
        own_name = infer_own_name(archive)
    data = parse_messages(archive, own_name)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'hangouts'
    log.info('Detecting languages...')
    df = detect_language(df)
    export_dataframe(df, config['hangouts']['OUTPUT_PICKLE_NAME'])
    log.info('Done.')


def parse_messages(archive, own_name):
    """
    Google Hangouts exports all the chat logs in a single JSON file. The format is super redundant and contains a lot of meta-information.
    {
      "conversations": [
        {
          "conversation": {
            "conversation_id": {
              "id": "<conversation_id>"
            },
            "conversation": {
              "id": {
                "id": "<conversation_id>"
              },
              "type": "TEXT",
              "participant_data": [
                {
                  "id": {<user ids>},
                  "fallback_name": "<plaintext name>",
                },
                ...data for each participant...
              ]
              ...more conversation-specific data...
            }
          },
          "events": [
            {
              "conversation_id": {
                "id": "<conversation_id>"
              },
              "timestamp": "<timestamp>",
              "chat_message": {
                "message_content": {
                  "segment": [
                    {
                      "type": "TEXT",
                      "text": "<actual text>"
                    }
                  ]
                }
              },
              ...other message-specific data...
            },
            ...other messages/events...
          ]
        },
        ...other conversations...
      ]
    }
    """
    id_to_name_map = {}

    def id_to_name(_id):
        if _id in id_to_name_map:
            return id_to_name_map[_id]
        else:
            return None

    def save_name_for_id(name, _id):
        if _id not in id_to_name_map:
            id_to_name_map[_id] = name
        elif id_to_name_map[_id] != name:
            log.info(f'Assuming {name} is {id_to_name_map[_id]}')

    data = []
    log.info('Extracting messages...')
    for conversation in archive['conversations']:
        conversation_with_id = ''

        # saves the fallback_name of all participants
        if 'conversation' in conversation['conversation']:
            for participant in conversation['conversation']['conversation']['participant_data']:
                if 'fallback_name' in participant:
                    save_name_for_id(participant['fallback_name'], participant['id']['chat_id'])

        for event in conversation['events']:
            if 'chat_message' in event and 'segment' in event['chat_message']['message_content']:
                timestamp = int(event['timestamp'])
                content = event['chat_message']['message_content']
                text = content['segment'][0]['text']
                conversation_id = event['conversation_id']['id']
                sender_id = event['sender_id']['chat_id']
                participants = conversation['conversation']['conversation']['current_participant']

                # no support for group chat
                if len(participants) == 2:
                    for participant in participants:
                        if id_to_name(participant['chat_id']) != own_name:
                            conversation_with_id = participant['chat_id']

                    sender_name = id_to_name(sender_id)
                    conversation_with_name = id_to_name(conversation_with_id)

                    if sender_name is not None or conversation_with_name is not None:

                        # checks that the sender is either own_name or the interlocutor
                        if sender_name != own_name and sender_id != conversation_with_id:
                            log.error(f'Parsing error. Is your own_name {own_name} correct?')
                            log.error(f'Problem: this message was sent by {sender_name}, who is not you ({own_name})')
                            log.error(f'It was sent by id {sender_id}, who is not your current interlocutor either ({conversation_with_id})')
                            log.error(f'Participants are: {participants}')
                            exit(0)

                        # saves the message
                        timestamp = timestamp / 1000000
                        outgoing = sender_name == own_name
                        conversation_with_name = conversation_with_name if conversation_with_name is not None else ''
                        sender_name = sender_name if sender_name is not None else ''
                        data += [[timestamp, conversation_id, conversation_with_name, sender_name, outgoing, text, '', '']]
                    else:
                        # unknown sender
                        log.error(f'No sender_name could be found for either sender_id ({sender_id}) or conversation_with_id ({conversation_with_id})')

                    if len(data) >= MAX_EXPORTED_MESSAGES:
                        log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                        return data
    return data


def read_archive(file_path):
    log.info(f'Reading archive file {file_path}...')
    with open(file_path, encoding='utf-8') as f:
        archive = json.loads(f.read())
    return archive


def infer_own_name(archive, min_conversations=2):
    '''Infers own name from multiple conversations by finding the person who participated most in the conversations'''
    participants_conversation_count = defaultdict(int)
    num_conversations = 0
    log.info('Trying to infer own_name from data...')
    for conversation in archive['conversations']:
        conversation_with_id = ''
        conversationWithName = ''
        if 'conversation' in conversation['conversation']:
            participants = conversation['conversation']['conversation']['participant_data']
            participants = [p['fallback_name'] for p in participants if 'fallback_name' in p]
            if len(participants) >= 2:
                num_conversations += 1
                for p in participants:
                    participants_conversation_count[p] += 1
    if num_conversations >= min_conversations and len(participants_conversation_count.keys()) >= 2:
        own_name = max(participants_conversation_count, key=participants_conversation_count.get)
        log.info(f'Successfully inferred own-name to be {own_name}')
        return own_name
    raise Exception('Could not infer own name from existing converstations. Please provide your username manually with the --own-name argument')
