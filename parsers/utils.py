import os
import datetime


def export_dataframe(df, filename='exported.pkl'):
    filepath = os.path.join('data', filename)
    print('Saving to pickle file %s...' % filepath)
    df.to_pickle(filepath)


def timestamp_to_ordinal(value):
    return datetime.datetime.fromtimestamp(float(value)).toordinal()
    ordinate = lambda x: datetime.datetime.fromtimestamp(float(x)).toordinal()
    df['datetime'] = df['timestamp'].apply(ordinate)
