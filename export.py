import argparse
import sys
import logging
from utils import ArgParseDefault, add_load_data_args, load_data
import pandas as pd
import os
from datetime import datetime
import pickle
from anonymisation.anonymize import pseudomize, anonymize

log = logging.getLogger(__name__)


def main():
    """Simple method to export message logs to either stdout or to a file"""

    def get_f_name(compressed):
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        f_path = os.path.join('exports', f'chatistics_export_{ts}.{args.format}')
        if compressed:
            f_path += '.zip'
        return f_path

    parser = ArgParseDefault(description='Export parsed chatlog data')
    parser = add_load_data_args(parser)
    parser.add_argument('-n', '--num-rows', dest='num_rows', type=int,
                        default=50, help='Print first n rows (use negative for last rows) (only used if output format is stdout)')
    parser.add_argument('-c', '--cols', dest='cols', nargs='+',
                        default=['timestamp', 'conversationWithName', 'senderName', 'outgoing', 'text', 'language', 'platform'],
                        help='Only show specific columns (only used if output format is stdout)')
    parser.add_argument('-f', '--format', dest='format', default='stdout', choices=['stdout', 'json', 'csv', 'pkl'], help='Output format')
    parser.add_argument('--compress', action='store_true', help='Compress the output (only used for json and csv formats)')
    parser.add_argument('--pseudomize', action='store_true', help='Hash sender and conversation names.')
    parser.add_argument('--anonymize', default='no', choices=['no','weak', 'medium', 'strong', 'all'], help='Replace senderNames with "<me>" (outgoing) and "<you>" (other) and conversation names with "<conversation>". Replace occurances of potentially identifying tokens for `medium`, `strong`, and `all` options (experimental and EN only!).')
    parser.add_argument('-s', '--sample', dest='sample', type=float, default=0, help='Take random sample. If arg >= 1 then n=int(arg). If 0 < arg < 1, the fraction arg of the whole data set is sampled. arg = 0 has no effect and all messages are exported.')
    parser.add_argument('--print-removed', dest='print_removed', action='store_true', help='Print removed tokens.')


    args = parser.parse_args()
    df = load_data(args)

    # filter EN messages for anonymization with 'medium', 'strong', and 'all' options
    # has to be done before sampling to not remove items from the sample
    if args.anonymize and args.anonymize != 'weak':
        # working for EN only!
        df = df[df.language=='en']

    if args.sample > 0:
        if args.sample < 1:
            df = df.sample(frac=args.sample)
        else:
            df = df.sample(min(int(args.sample), len(df)))
        log.info(f'Took random sample with n={len(df)}.')

    if args.pseudomize:
        df = pseudomize(df, args)

    if args.anonymize != 'no':
        df = anonymize(df, args)

    if args.format == 'stdout':
        # Print data to stdout
        df = df.iloc[:args.num_rows]
        df.loc[:, 'timestamp'] = pd.to_datetime(df.timestamp, unit='s')
        pd.set_option('display.max_colwidth', 100)
        with pd.option_context('display.max_rows', 1000, 'display.width', -1):
            print(df[args.cols].to_string(index=False))
    else:
        # Exporting data to a file
        f_name = get_f_name(args.compress)
        log.info(f'Exporting data to file {f_name}')
        compression = 'zip' if args.compress else None
        if args.format == 'json':
            df.to_json(f_name, orient='records', compression=compression)
        elif args.format == 'csv':
            df.to_csv(f_name, index=False, compression=compression)
        elif args.format == 'pkl':
            with open(f_name, 'wb') as f:
                pickle.dump(df, f)
        else:
            raise Exception(f'Format {args.format} is not supported.')


if __name__ == '__main__':
    main()
