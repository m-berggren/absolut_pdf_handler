import json
import os
import shutil

import pdf_parser
import sqlite_db

ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']

conn = sqlite_db.create_connection(directories['db_file'])
pdf_directory = directories['pdf_dir']
log_filename = directories['log_file']

full_pdf_path = os.path.join(ROOT_DIR, directories['pdf_dir'].replace("/", "\\"))
move_to_dir = os.path.join(ROOT_DIR, directories['move_to_dir'].replace("/", "\\"))
not_readable_dir = os.path.join(ROOT_DIR, directories['not_readable_dir'].replace("/", "\\"))


def loop_all_pdfs(conn, directory):
    """
    Loops through all pdf files in directory and run 'pdf_parser.py',
    'sqlite_db.py' on each iteration.

    :param conn: connection to SQLite .db file.
    :param directory: directory to all PDFs, in 'config.json'.
    """

    """
    To check SQLite .db in Cmder:
        sqlite3 + path to .db file
        .header on
        .mode column
        SELECT * FROM bookings;
    """
    print(f'{"REF":^15}|{"EQU":^13}|{"NWT":^10}|{"MRN":^20}|{"PKG":^6}|{"ABS":^10}|{"DAT":^12}')

    for filename in os.listdir(directory):

        if filename.endswith('.pdf') and filename.startswith('(1)'):
            booking = pdf_parser.create_booking(filename)

            if booking[1]:
                sqlite_db.create_booking(conn, booking, log_filename)
                shutil.move(os.path.join(full_pdf_path, filename), move_to_dir)
    
                print(f'{booking[0]:^15}|{booking[1]:^13}|{booking[2]:^10}|{booking[3]:^20}|{booking[4]:^6}|{booking[5]:^10}|{booking[6]:^12}')

            else:
                continue
        else:
            if filename == ".gitkeep": continue
            shutil.move(os.path.join(full_pdf_path, filename), not_readable_dir)
            print("No PDF and/or does not start with (1)")
            
    conn.close()

def delete_all_bookings(conn):
    """
    Removes all booking data from SQLite .db file.
    
    :param conn: connection to SQLite .db file.
    """
    sqlite_db.delete_all_bookings(conn)

def delete_booking_by_id(conn, id):
    """
    Removes row id from SQLite .db file.
    
    :param conn: connection to SQLite .db file.
    :param id: what row id to remove in .db file.
    """
    sqlite_db.delete_booking(conn, id)

loop_all_pdfs(conn, pdf_directory)
#delete_all_bookings(conn)