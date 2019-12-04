import os
import datetime

log = logging.getLogger(__name__)

def export_dataframe(df, filename='exported.pkl'):
    filepath = os.path.join('data', filename)
    log.info(f'Saving to pickle file {filepath}...')
    df.to_pickle(filepath)


def timestamp_to_ordinal(value):
    return datetime.datetime.fromtimestamp(float(value)).toordinal()
