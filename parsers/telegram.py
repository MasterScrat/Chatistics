#!/usr/bin/env python3
import argparse
import logging

import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat

from parsers import utils, config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--own-name', dest='own_name', type=str,
                        help='name of the owner of the chat logs, written as in the logs', required=True)
    parser.add_argument('-f', '--file-path', dest='file_path', help='Facebook chat log file (HTML file)',
                        default='raw/messages')
    parser.add_argument('--max', '--max-exported-messages', dest='max_exported_messages', type=int,
                        default=config.MAX_EXPORTED_MESSAGES, help='maximum number of messages to export')
    args = parser.parse_args()
    return args


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt=logging.BASIC_FORMAT))
log.addHandler(handler)


def list_dialogs(client):
    dialogs = client.get_dialogs()
    for item in dialogs:
        dialog = item.dialog
        if isinstance(dialog.peer, PeerUser):
            process_dialog_with_user(client, dialog)
        elif isinstance(dialog.peer, (PeerChannel, PeerChat)):
            log.debug('Dialogs in chats/channels are not supported yet')
        else:
            log.warning('Unknown dialog type %s', dialog)

    return []


def sign_in(client):
    print('Logging into account {}...'.format(config.TELEGRAM_PHONE))
    if not client.is_user_authorized():
        client.send_code_request(config.TELEGRAM_PHONE)
        code = input('Enter code received: ')
        me = client.sign_in(code=code)
    else:
        me = client.get_me()
    return me


def process_dialog_with_user(client, dialog):
    user_id = dialog.peer.user_id
    limit = config.TELEGRAM_USER_DIALOG_MESSAGES_LIMIT
    import pdb; pdb.set_trace()
    result = []
    messages = client.get_message_history(user_id, limit=limit)
    for message in messages:
        timestamp = message.date.timestamp()
        ordinal_date = message.date.toordinal()
        text = message.message
        conversation_id = 1
        conversation_with_name = 'Unknown'
        sender_name = 'Me'
        result.append([timestamp, ordinal_date, text, conversation_id, conversation_with_name, sender_name, text])
    return result


def main():
    client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    client.connect()
    me = sign_in(client)
    data = list_dialogs(client)
    print('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
    df['platform'] = 'telegram'

    utils.export_dataframe(df, 'telegram.pkl')
    print('Done.')


if __name__ == '__main__':
    main()

