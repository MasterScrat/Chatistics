import os


def export_dataframe(df, filename='exported.pkl'):
    filepath = os.path.join('data', filename)
    print('Saving to pickle file %s...' % filepath)
    df.to_pickle(filepath)
