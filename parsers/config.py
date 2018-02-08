import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))

DATAFRAME_COLUMNS = ['timestamp', 'conversationId', 'conversationWithName', 'senderName', 'text']
MAX_EXPORTED_MESSAGES = 1000000


DEFAULT_HANGOUTS_RAW_FILE = os.path.join(ROOT_DIR, 'raw/Hangouts.json')
DEFAULT_MESSENGER_RAW_FILE = os.path.join(ROOT_DIR, 'raw/messages')
