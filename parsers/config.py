import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))

ALL_COLUMNS = [
    'timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text', 'language', 'platform', 'datetime'
]
DATAFRAME_COLUMNS = ['timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text']
MAX_EXPORTED_MESSAGES = 1000000


# Google Hangouts
DEFAULT_HANGOUTS_RAW_FILE = os.path.join(ROOT_DIR, 'raw/Hangouts.json')


# Facebook messenger
DEFAULT_MESSENGER_RAW_FILE = os.path.join(ROOT_DIR, 'raw/messages')


# Telegram
TELEGRAM_API_ID = '<paste api_id here>'
TELEGRAM_API_HASH = '<paste api_hash here>'
TELEGRAM_PHONE = '<paste your phone number here>'

TELEGRAM_USER_DIALOG_MESSAGES_LIMIT = 1000
