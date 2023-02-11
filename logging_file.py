import logging

def debug_logger(values, filename):
    """
    Every time PDF parser run and data is stored to SQLite Db file,
    a log is saved to {filename} from 'config.json' with time,
    name, level and info from the booking.

    :param values: data (ref, equ, nwt, mrn, pkg, abs) from 'pdf_parser.py'
    :param filename: name and possibly dir of the logging file in 'config.cfg'
    """

    logging.basicConfig(
        filename=filename,
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
        )
    logging.debug(values)