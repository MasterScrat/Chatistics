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
    parser.add_argument('--anonymize', default=None, choices=['weak', 'strong', 'all'], help='Replace senderNames with "<me>" (outgoing) and "<you>" (other) and conversation names with "<conversation>". Further, replace occurances of potentially identifying tokens for `strong` and `all` options (experimental and EN only!).')
    parser.add_argument('-s', '--sample', dest='sample', type=float, default=0, help='Take random sample of size n.')

    args = parser.parse_args()
    df = load_data(args)


    # filter EN messages for anonymization with 'strong' and 'all' options
    # has to be done before sampling to not remove items from the sample
    if args.anonymize and args.anonymize != 'weak':
        # working for EN only!
        df = df[df.language=='en']

    if args.sample > 0:
        if args.sample <= 1:
            df = df.sample(frac=args.sample)
        else:
            df = df.sample(min(int(args.sample), len(df)))
        log.info(f'Took random sample with n={len(df)}.')


    if args.pseudomize:
        import hashlib
        df.conversationWithName = [x.hexdigest() for x in map(hashlib.sha256, df.conversationWithName.str.encode('utf-8'))]
        df.senderName = [x.hexdigest() for x in map(hashlib.sha256, df.senderName.str.encode('utf-8'))]

    if args.anonymize:
        # replace user names
        df.conversationWithName = '<conversation>'
        df.senderName = ['<me>' if x else '<you>' for x in df.outgoing]

        # also remove potenitally sensitive or identifiable information in messages
        if args.anonymize != 'weak': # 'strong' and 'all' options
            # log warning for these options
            log.warn('/!\ The `strong` and `all` options for the anonymize feature are experimental and will export messages in English only.')
            log.warn('/!\ Using this anonymization does ot garuantee that all dientifiable or sensitive information will be removed!')
            # import anonymize-only packages
            import spacy
            import re
            from functools import partial
            from tqdm import tqdm

            # function that will be applied to every message in the data frame
            def remove_identifyers(nlp, args, regs, text):
                # return empty string if text is None or empty
                if not text:
                    return ""
                # remove telephone numbers, emails, IBAN, and credit card numbers
                for key, reg in regs.items():
                    # replace occurances of patterns in text
                    text = re.sub(reg, f'<{key}>', text)
                # process message with spacy nlp
                doc = nlp(text)
                # remove words that are recognized as proper noun
                tokens = [token.text if token.pos_ not in ['PROPN'] else f'<{token.pos_}>' for token in doc]
                # remove named entities
                # 'strong' removes certain types of entities while 'all' removes all recongized entities including amounts of money etc. see https://spacy.io/api/annotation for all types.
                entities = {entity.text: '<' + entity.label_ + '>' for entity in doc.ents if entity.label_ in ['PERSON','NORP','FAC','GPE','LOC','EVENT','DATE'] or args.anonymize == 'all'}
                tokens = [token if token not in entities else entities[token] for token in tokens]
                # join tokens to text again
                text = ' '.join(tokens)
                # return text with replaced tokens
                return text

            # load spacy en langauge model
            try:
                nlp = spacy.load("en_core_web_sm")
            except:
                sys.exit('!!! `en_core_web_sm` not available. run `python -m spacy download en_core_web_sm` first.')

            # allows pandas to show processing progress with tqdm
            tqdm.pandas()
            # some regex patterns to remove email, iban, payment card numbers, phone numbers, social media handles
            # the regexes are simplified, might not catch all relevant info but might also catch irrelevant!
            regs = {
                'EMAIL': re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,4}'),
                'IBAN': re.compile(r'([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?'),
                'CARD': re.compile(r'[1-9][0-9 .\-]{6,17}[0-9]'),
                'PHONE': re.compile(r'(\+|00)?[0-9 .\-\']{2,14}[0-9]'),
                'HANDLE': re.compile(r'@[\-_.\w]+')
            }
            # add cases above to tokenizer
            for key, reg in regs.items():
                nlp.tokenizer.add_special_case(f'<{key}>', [{'ORTH': f'<{key}>'}])
            # remove potentially harmful info as good as possible
            df.text = df.text.progress_apply(partial(remove_identifyers, nlp, args, regs))

            log.info(f'Anonymized {len(df)} messages.')


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
