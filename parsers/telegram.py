#!/usr/bin/env python3s
import argparse
import pandas as pd

from parsers import config, utils


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--own-name', dest='own_name', type=str,
                        help='name of the owner of the chat logs, written as in the logs', required=True)
    parser.add_argument('-f', '--file-path', dest='file_path', help='Facebook chat log file (HTML file)',
                        default='raw/messages')
    parser.add_argument('--max', '--max-exported-messages', dest='max_exported_messages', type=int,
                        default=config.MAX_EXPORTED_MESSAGES, help='maximum number of messages to export')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    data = []
    print('Converting to DataFrame...')
    df = pd.DataFrame(data)
    df.columns = config.DATAFRAME_COLUMNS
    df['platform'] = 'telegram'
    utils.export_dataframe(df, 'telegram.pkl')


if __name__ == '__main__':
    main()
