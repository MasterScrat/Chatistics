import re
import logging
from visualizers.utils import save_fig
from utils import load_data
from collections import Counter
import itertools
import numpy as np

log = logging.getLogger(__name__)
EMOJI_PATTERN = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

def main(args):
    # load data
    df = load_data(args)
    log.info(f'Computing emoji frequencies on {len(df):,} messages... 😤')
    # Compute emoji frequencies
    freqs = compute_emoji_freqs(df)
    print_emoji_freqs(freqs, top_n_users=args.top_n_users, top_n_emojis=args.top_n_emojis)

def compute_emoji_freqs(df):
    df.loc[:, 'emojis'] = df.text.str.findall(EMOJI_PATTERN)
    df.dropna(subset=['emojis'], inplace=True)
    df = df.loc[df.emojis.apply(lambda s: len(s)) > 0, ['emojis', 'senderName', 'outgoing']]
    df.loc[:, 'emojis'] = df.emojis.apply(lambda s: list(''.join(s)))
    num_emojis = df.emojis.apply(lambda s: len(s)).sum()
    log.info(f'Found {len(df):,} messages containing {num_emojis:,} emojis! 🤗🤗')
    df.loc[df['outgoing'], 'senderName'] = 'You'
    freqs = {}
    for name, group in df.groupby('senderName'):
        emojis = group.emojis.tolist()
        freqs[name] = Counter(itertools.chain.from_iterable(emojis))
    return freqs

def print_emoji_freqs(freqs, top_n_users=10, top_n_emojis=10):
    # selecting top n emoji users
    by_user = {k: sum(c.values()) for k, c in freqs.items()}
    top_users = [c[0] for c in Counter(by_user).most_common(top_n_users)]
    # print out top users emoji usage
    for user in top_users:
        print(f'Favorite emojis for {user}')
        emojis = ' '.join([emoji for emoji, count in freqs[user].most_common(top_n_emojis)])
        print(emojis)
