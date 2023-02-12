import json
import os

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
    print(f'{"REF":<13} | {"EQU":<11} | {"NWT":8} | {"MRN":<18} | {"PKG":<4} | {"ABS":<8}')

    for filename in os.listdir(directory):

        if filename.endswith('.pdf') and filename.startswith('(1)'):
            booking = pdf_parser.create_booking(filename)

            if booking[1]:
                sqlite_db.create_booking(conn, booking, log_filename)
                print(f'{booking[0]:<13} | {booking[1]:<11} | {booking[2]:<5.2f} | {booking[3]:18} | {booking[4]:<4} | {booking[5]:8}')

            else:
                continue
        else:
            print("No PDF and/or does not start with (1)")

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