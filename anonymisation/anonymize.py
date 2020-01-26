import pandas as pd
import hashlib
import spacy
import re
from functools import partial
from tqdm import tqdm

import logging
log = logging.getLogger(__name__)

# function that will be applied to every message in the data frame
def _remove_identifyers(nlp, args, regs, types, text):
    # return empty string if text is None or empty
    if not text:
        return ""
    # we keep the removed tokens for informative puproses
    removed = []
    # remove telephone numbers, emails, IBAN, and credit card numbers
    for key, reg in regs.items():
        # add removed tokens
        removed += [(x.group(0), f'<{key}>') for x in re.finditer(reg, text)]
        # replace occurances of patterns in text with <TYPE>
        text = re.sub(reg, f'<{key}>', text)
    # process message with spacy nlp
    doc = nlp(text)
    # removed named entities
    entities = {entity.text: '<' + entity.label_ + '>' for entity in doc.ents if entity.label_ in types or args.anonymize == 'all'}
    # additional safegaurds for option 'all'
    if args.anonymize == 'all':
        # remove tokens that are recognized as proper nouns but not as named entities
        for token in doc:
            if token.pos_ == 'PROPN' and token.text not in entities:
                entities[token.text] = f'<{token.tag_}>'
    # remove entities
    for key, rep in entities.items():
        # add removed tokens
        removed.append((key, rep))
        # replace occurances of entities in text with <TYPE>
        text = text.replace(key, rep)
    # return anonymized text
    return text, removed


def pseudomize(df, args):
    df.conversationWithName = [x.hexdigest() for x in map(hashlib.sha256, df.conversationWithName.str.encode('utf-8'))]
    df.senderName = [x.hexdigest() for x in map(hashlib.sha256, df.senderName.str.encode('utf-8'))]
    return df


def anonymize(df, args):
    # replace user and conversation names
    if args.anonymize != 'all': # keep distinction among other speakers
        # replace conversation names
        conversation_names = {}
        for i, name in enumerate(df.conversationWithName.unique(), start=1):
            conversation_names[name] = f'<conversation{i}>'
        df.conversationWithName = [conversation_names[name] for name in df.conversationWithName]
        # replace user names
        sender_names = {}
        for i, name in enumerate(df[df.outgoing==False].senderName.unique(), start=1):
            sender_names[name] = f'<you{i}>'
        df.senderName = ['<me>' if outgoing else sender_names[name] for name, outgoing in df[['senderName','outgoing']].itertuples(index=False)]
    else: # omit distinction among other speakers
        df.conversationWithName = '<conversation>'
        df.senderName = ['<me>' if x else '<you>' for x in df.outgoing]

    # also remove potenitally sensitive or identifiable information in messages
    if args.anonymize != 'weak': # 'medium', 'strong', and 'all' options
        # log warning for these options
        log.warn('/!\ The `medium`, `strong`, and `all` options for the anonymize feature are experimental and will export messages in English only.')
        log.warn('/!\ Using this anonymization does ot guarantee that all identifiable or sensitive information will be removed!')

        # load spacy en langauge model
        try:
            # nlp = spacy.load("xx_ent_wiki_sm")
            nlp = spacy.load("en_core_web_sm")
        except:
            sys.exit('!!! `en_core_web_sm` not available. run `python -m spacy download en_core_web_sm` first.')

        # allows pandas to show processing progress with tqdm
        tqdm.pandas()

        # some regex patterns to remove email, iban, payment card numbers, phone numbers, social media handles
        # the regexes are simplified, might not catch all relevant info but might also catch irrelevant!
        regs = {
            'EMAIL': re.compile(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,4}', flags=re.IGNORECASE),
            'IBAN': re.compile(r'([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?', flags=re.IGNORECASE),
            'CARD': re.compile(r'[1-9][0-9]{3}([ .\-]?[0-9]{4}){2}[ .\-]?[0-9]{4}'),
            'PHONE': re.compile(r'((\+|\(?00)[1-9][0-9]{0,2}\)?[ .\-\']{0,3})?\(?[0-9]{1,3}\)?([ .\-\']?[0-9]{2,5}){2,4}'),
            'HANDLE': re.compile(r'@[\-_.\w]+'),
        }
        # add regex cases to tokenizer as special tokens
        for key, reg in regs.items():
            nlp.tokenizer.add_special_case(f'<{key}>', [{'ORTH': f'<{key}>'}])

        # types of named entitites that will be removed. 'medium' and 'strong' removes certain types of named entities while 'all' removes all types.
        # See https://spacy.io/api/annotation for all types.
        if args.anonymize == 'medium':
            types = ['PERSON','PER']
        elif args.anonymize == 'strong':
            types = ['PERSON','PER','NORP','FAC','GPE','LOC','EVENT','DATE']
        else:
            types = []

        # remove potentially harmful info as good as possible
        anonymized = df.text.progress_apply(partial(_remove_identifyers, nlp, args, regs, types))
        dfa = pd.DataFrame()
        dfa[['text','removed']] = pd.DataFrame(anonymized.tolist(), index=df.index)
        # get removed tokens
        removed = [r for rs in dfa.removed for r in rs]

        # log removed tokens
        if args.print_removed:
            removed_str = "\n".join([str(t) for t in set(removed)][:args.num_rows])
            log.info(f'Removed tokens:\n{removed_str}')

        # replace original message with anonymized message
        df.text = dfa.text
        log.info(f'Anonymized {len(df)} messages. {len(set(removed))} unique / {len(removed)} total tokens removed.')
    return df
