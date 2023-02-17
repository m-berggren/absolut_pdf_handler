import json
import logging
import os

def directory():

    ROOT_DIR = os.path.abspath('')
    config_path = '\\'.join([ROOT_DIR, 'config.json'])

    with open(config_path) as cfile:
        config = json.load(cfile)
    
    return config['directories']
    

#def booking_logger(message):
#    """
#    Every time PDF parser run and data is stored to SQLite Db file,
#    a log is saved to {filename} from 'config.json' with time,
#    name, level and info from the booking.
#
#    :param msg: data (ref, equ, nwt, mrn, pkg, abs) from 'pdf_parser.py' or something else.
#    :param filename: name and possibly dir of the logging file in 'config.cfg'
#    """
#
#    logging.basicConfig(
#        filename=directory()['bookings_log'],
#        encoding='utf-8',
#        format='%(asctime)s : %(levelname)s : %(funcname)s : %(message)s',
#        level=logging.DEBUG
#        )
#    logging.debug(message)


def pdf_parser_logger():

    dir = directory()
    logger = logging.getLogger(__name__)

    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(funcname)s : %(message)s')

    file_handler = logging.FileHandler(dir['debug_pdf_parser'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def sqlite_logger():

    dir = directory()
    logger = logging.getLogger(__name__)

    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(funcname)s : %(message)s')

    file_handler = logging.FileHandler(dir['debug_sqlite_db'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def outlook_logger():

    dir = directory()
    logger = logging.getLogger(__name__)

    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(funcname)s : %(message)s')

    file_handler = logging.FileHandler(dir['debug_outlook_dl'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def general_logger():

    dir = directory()
    logger = logging.getLogger(__name__)

    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(funcname)s : %(message)s')

    file_handler = logging.FileHandler(dir['debug_general_log'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def bookings_logger(formatter):

    dir = directory()
    logger = logging.getLogger(__name__)

    #formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(funcname)s : %(message)s')

    file_handler = logging.FileHandler(dir['bookings_log'])
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)