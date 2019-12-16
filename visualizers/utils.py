import os
import time
import logging

log = logging.getLogger(__name__)

def save_fig(fig, name, output_formats=('png',)):
    date = time.strftime('%Y%m%d')
    ts = int(time.time() * 1000)
    for fmt in output_formats:
        save_name = os.path.join('plots', f'{name}_{fmt}_{ts}.{fmt}')
        log.info(f'Saving figure as {save_name}')
        fig.savefig(save_name)

