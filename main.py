import json
import os
import logging
import shutil
from tqdm import tqdm

import pdf_parser
import sqlite_db

ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
file_handler = logging.FileHandler(directories['debug_general_log'])
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

conn = sqlite_db.create_connection(directories['db_file'])
pdf_directory = directories['pdf_dir']

full_pdf_path = os.path.join(ROOT_DIR, directories['pdf_dir'].replace("/", "\\"))
move_to_dir = os.path.join(ROOT_DIR, directories['move_to_dir'].replace("/", "\\"))
not_readable_dir = os.path.join(ROOT_DIR, directories['not_readable_dir'].replace("/", "\\"))
duplicates_dir = os.path.join(ROOT_DIR, directories['duplicate_bookings'].replace("/", "\\"))


def loop_all_pdfs(conn):
    """
    Loops through all pdf files in directory and run 'pdf_parser.py',
    'sqlite_db.py' on each iteration.

    :param conn: connection to SQLite .db file.
    :param directory: directory to all PDFs, in 'config.json'.
    """

    """
    Check SQLite Db in terminal:
        sqlite3 + path to .db file
        .header on
        .mode column
        SELECT * FROM bookings;
    """


    for filename in tqdm(os.listdir(pdf_directory), desc='Parsed PDF counter', unit='PDFs'):

        if filename.endswith('.pdf') and filename.startswith('(1)'):
            booking = pdf_parser.create_booking(filename)
            equipment = booking[1]
            
            if equipment:
                sqlite_db.execute_sqlite(conn, booking)
                try:
                    shutil.move(os.path.join(full_pdf_path, filename), os.path.join(move_to_dir, filename))
                except (PermissionError, shutil.Error)as e:
                    logger.debug(e)

            else:
                try:
                    shutil.move(os.path.join(full_pdf_path, filename), os.path.join(not_readable_dir, filename))
                    logger.info(f'No container number found in {filename}, moved to {os.path.basename(not_readable_dir)}.')

                except (PermissionError, shutil.Error)as e:
                    logger.debug(e)
                
        else:
            if filename == ".gitkeep": continue

            try:
                shutil.move(os.path.join(full_pdf_path, filename), os.path.join(not_readable_dir, filename))
                logger.info(f'{filename} is no PDF and/or does not start with (1), moved to {os.path.basename(not_readable_dir)}.')
            except (PermissionError, shutil.Error)as e:
                logger.debug(e)

    conn.close()
    logging.shutdown()

def delete_all_bookings(conn):
    """
    Removes all booking data from SQLite Db file, bookings.log
    and move all PDF files back to download folder.

    :param conn: connection to SQLite .db file.
    """

    logging.shutdown()

    sqlite_db.delete_all_bookings(conn)
    print(directories['bookings_log'])
    if os.path.isfile(directories['bookings_log']):
        os.remove(directories['bookings_log'])

    if os.path.isfile(directories['debug_general_log']):
        os.remove(directories['debug_general_log'])

    if os.path.isfile(directories['debug_sqlite_db']):
        os.remove(directories['debug_sqlite_db'])

    if os.path.isfile(directories['debug_outlook_dl']):
        os.remove(directories['debug_outlook_dl'])


    for filename in tqdm(os.listdir(move_to_dir), desc='Moving PDF counter', unit='PDFs'):

        if filename == ".gitkeep": continue
        try:
            shutil.move(os.path.join(move_to_dir, filename), os.path.join(full_pdf_path))
        except (PermissionError, shutil.Error) as e:
            logger.debug(e)

    for filename in os.listdir(not_readable_dir):
        if filename == ".gitkeep": continue
        if filename.startswith('(1)'):
            try:
                shutil.move(os.path.join(not_readable_dir, filename), os.path.join(full_pdf_path, filename))
            except (PermissionError, shutil.Error)as e:
                logger.debug(e)


def delete_booking_by_id(conn, id):
    """
    Removes row id from SQLite .db file.

    :param conn: connection to SQLite .db file.
    :param id: what row id to remove in .db file.
    """
    sqlite_db.delete_booking(conn, id)

if __name__ == '__main__':
    loop_all_pdfs(conn)
    #delete_all_bookings(conn)