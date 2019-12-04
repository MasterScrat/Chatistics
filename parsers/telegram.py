import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat
from parsers.utils import export_dataframe
from parsers.config import config
import logging

log = logging.getLogger(__name__)

async def list_dialogs(client, own_name):
    result = []
    async for item in client.iter_dialogs():
        if len(result) > MAX_EXPORTED_MESSAGES:
            return result
        dialog = item.dialog
        if isinstance(dialog.peer, PeerUser):
            _r = await process_dialog_with_user(client, item, own_name)
            result.extend(_r)
        elif isinstance(dialog.peer, (PeerChannel, PeerChat)):
            log.info('Dialogs in chats/channels are not supported yet')
        else:
            log.warning('Unknown dialog type %s', dialog)
    return result

async def process_dialog_with_user(client, item, own_name):
    result = []
    conversation_with_name = item.name

    # deleted account
    if conversation_with_name == '': return result

    dialog = item.dialog
    user_id = dialog.peer.user_id
    async for message in client.iter_messages(user_id, limit=USER_DIALOG_MESSAGES_LIMIT):
        timestamp = message.date.timestamp()
        ordinal_date = message.date.toordinal()
        text = message.message
        if message.out:
            sender_name = own_name
        else:
            sender_name = conversation_with_name
        result.append([timestamp, user_id, conversation_with_name, sender_name, message.out, text, 'unknown', '', ordinal_date])
    return result

async def _main_loop(client):
    me = await client.get_me()
    first_name = ''
    last_name = ''
    if me.first_name is not None:
        first_name = me.first_name
    if me.last_name is not None:
        last_name = me.last_name
    own_name = '{} {}'.format(first_name, last_name).strip()
    data = await list_dialogs(client, own_name)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'telegram'
    log.info('Detecting languages...')
    df['language'] = 'unknown'
    export_dataframe(df, 'telegram.pkl')
    log.info('Done.')

def main(max_exported_messages=10000, user_dialog_messages_limit=1000):
    global MAX_EXPORTED_MESSAGES
    global USER_DIALOG_MESSAGES_LIMIT
    MAX_EXPORTED_MESSAGES = max_exported_messages
    USER_DIALOG_MESSAGES_LIMIT = user_dialog_messages_limit
    with TelegramClient('session_name', config['TELEGRAM_API_ID'], config['TELEGRAM_API_HASH']) as client:
        client.loop.run_until_complete(_main_loop(client))
