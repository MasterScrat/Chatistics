#!/usr/bin/env python3
import sys

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.\n")
    sys.exit(1)

import pandas as pd
from groupy import Client

from parsers import log
from parsers import utils, config


def list_direct_messages(client):
    chats = list(client.chats.list_all())
    result = []

    for chat in chats:
        result.extend(process_direct_message(chat))
    return result


def process_direct_message(chat):
    result = []
    conversation_with_name = chat.other_user['name']
    user_id = chat.other_user['id']

    for message in chat.messages.list_all():

        timestamp = message.created_at.timestamp()
        ordinal_date = message.created_at.toordinal()
        text = message.text
        result.append(
            [timestamp, user_id, conversation_with_name, '', text, 'unknown', 'groupme', ordinal_date])
    return result


def main():
    client = Client.from_token(config.GROUPME_API_TOKEN)
    data = list_direct_messages(client)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.ALL_COLUMNS
    # import pdb; pdb.set_trace()
    df['platform'] = 'groupme'
    own_name = client.user.me['name'].strip()
    df['senderName'] = own_name

    log.info('Detecting languages...')
    df['language'] = 'unknown'

    utils.export_dataframe(df, 'groupme.pkl')
    log.info('Done.')


if __name__ == '__main__':
    main()

