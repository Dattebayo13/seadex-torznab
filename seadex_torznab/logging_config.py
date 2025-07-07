import logging

def setup_logging():
    logging.basicConfig(
        filename='seadex_torznab.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
    ) 