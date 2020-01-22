import os
import time
import logging
import json

log = logging.getLogger(__name__)


def save_fig(fig, name, output_formats=('png',), dpi=300):
    """Save figure with timestamps"""
    date = time.strftime('%Y%m%d')
    ts = int(time.time() * 1000)
    for fmt in output_formats:
        save_name = os.path.join('plots', f'{name}_{ts}.{fmt}')
        log.info(f'Saving figure as {save_name}')
        fig.savefig(save_name, dpi=dpi)


def get_stopwords(stopword_paths):
    """Load stopwords given a stopword path"""
    stopwords = []
    for stopword_path in stopword_paths:
        log.info(f'Loading stopwords from {stopword_path}...')
        with open(stopword_path, 'r', encoding="utf8") as f:
            stopword_data = json.load(f)
        stopwords.extend(stopword_data)
    stopwords = list(set(stopwords))
    log.info(f'Loaded {len(stopwords):,} stopwords')
    return stopwords
