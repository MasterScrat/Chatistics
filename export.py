import argparse
import sys
import logging
from utils import ArgParseDefault, add_load_data_args, load_data
import pandas as pd
import os
from datetime import datetime
import pickle

log = logging.getLogger(__name__)

def main():
    """Simple method to export message logs to either stdout or to a file"""
    def get_f_name():
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        f_path = os.path.join('exports', f'chatistics_export_{ts}.{args.format}')
        return f_path

    parser = ArgParseDefault(description='Export parsed chatlog data')
    parser = add_load_data_args(parser)
    parser.add_argument('-n', '--num-rows', dest='num_rows', type=int,
            default=50, help='Print first n rows (use negative negative for last rows) (only used if output format is stdout)')
    parser.add_argument('-c', '--cols', dest='cols', nargs='+', default=['timestamp', 'conversationWithName', 'senderName', 'outgoing', 'text', 'language', 'platform'],
                        help='Only show specific columns (only used if output format is stdout)')
    parser.add_argument('-f', '--format', dest='format', default='stdout', choices=['stdout', 'json', 'csv', 'pkl'],  help='Output format')
    args = parser.parse_args()
    df = load_data(args)
    if args.format == 'stdout':
        # Print data to stdout
        df = df.iloc[:args.num_rows]
        df.loc[:, 'timestamp'] = pd.to_datetime(df.timestamp, unit='s')
        pd.set_option('display.max_colwidth', 100)
        with pd.option_context('display.max_rows', 1000, 'display.width', -1):
            print(df[args.cols].to_string(index=False))
    else:
        # Exporting data to a file
        f_name = get_f_name()
        log.info(f'Exporting data to file {f_name}')
        if args.format == 'json':
            df.to_json(f_name, orient='records')
        elif args.format == 'csv':
            df.to_csv(f_name, index=False)
        elif args.format == 'pkl':
            with open(f_name, 'wb') as f:
                pickle.dump(df, f)
        else:
            raise Exception(f'Format {args.format} is not supported.')

if __name__ == '__main__':
    main()
