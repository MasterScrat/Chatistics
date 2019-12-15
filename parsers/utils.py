import os
import datetime
import logging
from langdetect import detect

log = logging.getLogger(__name__)

def export_dataframe(df, filename):
    filepath = os.path.join('data', filename)
    log.info(f'Saving to pickle file {filepath}...')
    df.to_pickle(filepath)


def timestamp_to_ordinal(value):
    return datetime.datetime.fromtimestamp(float(value)).toordinal()


def detect_language(df, min_token_count=5):
    """Detects language of input text"""
    for name, group in df.groupby(df.conversationWithName):
        text = ' '.join(group['text'].dropna().values[:100])
        if len(text.split()) >= min_token_count:
            lang = detect(text)
        else:
            lang = 'unknown'
        df.loc[group.index, 'language'] = lang
    return df
