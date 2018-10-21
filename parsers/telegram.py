#!/usr/bin/env python3
import sys

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.\n")
    sys.exit(1)

import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat

from parsers import log
from parsers import utils, config


def list_dialogs(client):
    dialogs = client.get_dialogs()
    result = []
    for item in dialogs:
        dialog = item.dialog
        if isinstance(dialog.peer, PeerUser):
            result.extend(process_dialog_with_user(client, item))
        elif isinstance(dialog.peer, (PeerChannel, PeerChat)):
            log.debug('Dialogs in chats/channels are not supported yet')
        else:
            log.warning('Unknown dialog type %s', dialog)

    return result


def sign_in(client):
    print('Logging into account {}...'.format(config.TELEGRAM_PHONE))
    if not client.is_user_authorized():
        client.send_code_request(config.TELEGRAM_PHONE)
        code = input('Enter code received: ')
        me = client.sign_in(code=code)
    else:
        me = client.get_me()
    return me


def process_dialog_with_user(client, item):
    result = []
    conversation_with_name = item.name

    # deleted account
    if conversation_with_name == '': return result

    dialog = item.dialog
    user_id = dialog.peer.user_id
    limit = config.TELEGRAM_USER_DIALOG_MESSAGES_LIMIT
    messages = client.get_message_history(user_id, limit=limit)
    for message in messages:
        timestamp = message.date.timestamp()
        ordinal_date = message.date.toordinal()
        text = message.message
        result.append([timestamp, user_id, conversation_with_name, '', text, 'unknown', '', ordinal_date])
    return result


def main():
    client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    client.connect()
    me = sign_in(client)
    data = list_dialogs(client)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.ALL_COLUMNS
    # import pdb; pdb.set_trace()
    df['platform'] = 'telegram'
    own_name = '{} {}'.format(me.first_name, me.last_name).strip()
    df['senderName'] = own_name

    log.info('Detecting languages...')
    df['language'] = 'unknown'

    utils.export_dataframe(df, 'telegram.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()

