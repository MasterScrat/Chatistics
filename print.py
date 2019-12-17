import argparse
import sys
import logging.config
from utils import ArgParseDefault, add_load_data_args, load_data
import pandas as pd


def main():
    """Simple method to print message logs"""
    parser = ArgParseDefault(description='Print parsed chatlog data')
    parser = add_load_data_args(parser)
    parser.add_argument('-n', '--num-rows', dest='num_rows', type=int, default=50, help= 'Print first n rows (negative for last rows)')
    parser.add_argument('-c', '--cols', dest='cols', nargs='+', default=['timestamp', 'conversationWithName', 'senderName', 'outgoing', 'text', 'language', 'platform'], help= 'Print first n rows (negative for last rows)')
    args = parser.parse_args()
    df = load_data(args)
    df = df.iloc[:args.num_rows]
    df.loc[:, 'timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    pd.set_option('display.max_colwidth', 100)
    with pd.option_context('display.max_rows', 1000, 'display.width', -1):
        print(df[args.cols].to_string(index=False))

if __name__ == '__main__':
    main()
