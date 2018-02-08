import csv
import logging

from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat

import config


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt=logging.BASIC_FORMAT))
log.addHandler(handler)


def list_dialogs(client):
    dialogs = client.get_dialogs()
    # import pdb; pdb.set_trace()
    for item in dialogs:
        dialog = item.dialog
        if isinstance(dialog.peer, PeerUser):
            process_dialog_with_user(dialog)
        elif isinstance(dialog.peer, (PeerChannel, PeerChat)):
            log.debug('Dialogs in chats/channels are not supported yet')
        else:
            log.warn('Unknown dialog type %s', dialog)


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
    total_messages, messages, users = client.get_message_history(user_id, limit=limit)
    # user = client.get_entity(user_id)
    print('Dialog with user', user_id)  # , user.first_name, user.last_name)


def main():
    client = TelegramClient('session_name', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
    client.connect()
    me = sign_in(client)
    list_dialogs(client)
    limit = None
    dd = client.get_message_history(me.id, limit=limit)
    import pdb; pdb.set_trace()
    total_messages, messages, users = client.get_message_history(me.id, limit=limit)
    header = ['id', 'from_id', 'to_id', 'date', 'message', 'is_media', 'is_edited']
    with open('message_history.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for message in messages:
            is_media = message.media is not None
            is_edited = message.edit_date is not None
            row = [message.id, message.from_id, message.to_id.user_id, message.date,
                   message.message, is_media, is_edited]
            writer.writerow(row)


if __name__ == '__main__':
    main()
