import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChannel, PeerChat
from parsers.utils import export_dataframe, detect_language
from parsers.config import config
import logging

log = logging.getLogger(__name__)


async def list_dialogs(client, own_name):
    result = []
    async for item in client.iter_dialogs():
        if len(result) > MAX_EXPORTED_MESSAGES:
            log.warning(f'Reached MAX_EXPORTED_MESSAGES of {MAX_EXPORTED_MESSAGES:,}!')
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
        text = message.message
        if message.out:
            sender_name = own_name
        else:
            sender_name = conversation_with_name
        result.append([timestamp, user_id, conversation_with_name, sender_name, message.out, text, '', ''])
        if len(result) % 1000 == 0:
            log.info(f'Parsed {len(result):,} telegram messages in conversation {conversation_with_name}...')
    if len(result) == USER_DIALOG_MESSAGES_LIMIT:
        log.warning(f'Reached USER_DIALOG_LIMIT of {USER_DIALOG_MESSAGES_LIMIT:,} for conversation with {conversation_with_name}!')
    return result


async def _main_loop(client):
    own_name = await get_own_name(client)
    data = await list_dialogs(client, own_name)
    log.info('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    log.info('Converting to DataFrame...')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df['platform'] = 'telegram'
    log.info('Detecting languages...')
    df = detect_language(df)
    export_dataframe(df, config['telegram_api']['OUTPUT_PICKLE_NAME'])
    log.info('Done.')


async def get_own_name(client):
    if OWN_NAME is not None:
        return OWN_NAME
    me = await client.get_me()
    first_name = ''
    last_name = ''
    if me.first_name is not None:
        first_name = me.first_name
    if me.last_name is not None:
        last_name = me.last_name
    own_name = '{} {}'.format(first_name, last_name).strip()
    log.info(f'Successfully inferred own-name to be {own_name}')
    return own_name


def main(own_name, max_exported_messages=10000, user_dialog_messages_limit=1000):
    global MAX_EXPORTED_MESSAGES
    global USER_DIALOG_MESSAGES_LIMIT
    global OWN_NAME
    MAX_EXPORTED_MESSAGES = max_exported_messages
    USER_DIALOG_MESSAGES_LIMIT = user_dialog_messages_limit
    OWN_NAME = own_name
    log.info('Parsing Telegram data...')
    with TelegramClient('session_name', config['TELEGRAM_API_ID'], config['TELEGRAM_API_HASH']) as client:
        client.loop.run_until_complete(_main_loop(client))
