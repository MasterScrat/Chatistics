import csv

from telethon import TelegramClient
from telethon.tl.types import PeerUser

import config


def list_dialogs(client):
    dialogs = client.get_dialogs()[0]
    for dialog in dialogs:
        if isinstance(dialog.peer, PeerUser):
            user_id = dialog.peer.user_id
            user = client.get_entity(user_id)
            print('Dialog with user', user_id, user.first_name, user.last_name)
        else:
            print(dialog.to_dict())


def print_message(message):
    print(message.message)


def main():
    client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    client.connect()

    # me = client.sign_in(code='27105')
    me = client.get_me()
    import pdb; pdb.set_trace()
    # target_user = client.get_entity(config.TARGET_USER_ID)
    limit = None
    total_messages, messages, users = client.get_message_history(me.user_id, limit=limit)
    header = ['id', 'from_id', 'to_id', 'date', 'message', 'is_media', 'is_edited']
    with open('message_history.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for message in messages:
            print_message(message)
            is_media = message.media is not None
            is_edited = message.edit_date is not None
            row = [message.id, message.from_id, message.to_id.user_id, message.date,
                   message.message, is_media, is_edited]
            writer.writerow(row)


if __name__ == '__main__':
    main()
