import json
import os
import sqlite3

import logging_file

def create_connection(db_file):
    """
    Create a database conneciton to a SQLite database.

    :param db_file: database file
    :return: connection object or None
    """

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    
    return conn

def create_table(conn, create_table_sql):
    """
    Create a table from the create_table_sql statement.

    :param conn: connection to the SQLite database
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """

    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def create_booking(conn, booking, log_filename):
    """
    Create a new booking into the bookings table,
    or if equ exists then update entire row.
    Prints data to a log file, with 'NEW' or 'UPDATE'.

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    :param log_filename: logging name from 'config.json'.
    :return: booking id.
    """

    cur = conn.cursor()
    cur.execute("SELECT id FROM bookings WHERE equ = ?", (booking[1],))
    data = cur.fetchone()
    m = booking

    if data is None:
        sql = ''' INSERT INTO bookings(ref, equ, nwt, mrn, pkg, abs)
                VALUES(?, ?, ?, ?, ?, ?) '''
        cur.execute(sql, booking)
        conn.commit()
        debug_format = f"NEW:    | {m[0]:<13} | {m[1]:11} | {m[2]:<5.2f} | {m[3]:18} | {m[4]:<4} | {m[5]:8}"

    elif data:
        update_booking(conn, booking)
        debug_format = f"UPDATE: | {m[0]:<13} | {m[1]:11} | {m[2]:<5.2f} | {m[3]:18} | {m[4]:<4} | {m[5]:8}"

    else:
        pass   
    
    #logging_file.debug_logger(debug_format, log_filename)

    return cur.lastrowid

def update_booking(conn, booking):
    """
    Update ref, nwt, mrn, pkg of a unit (equ).

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    """

    sql = ''' UPDATE bookings
                SET ref = ? ,
                    nwt = ? ,
                    mrn = ? ,
                    pkg = ? ,
                    abs = ?
                WHERE equ = ? '''
    cur = conn.cursor()
    cur.execute(sql, booking)
    conn.commit()

def delete_booking(conn, id):
    """
    Delete booking by booking id.

    :param conn: connection to the SQLite database.
    :param id: id of the booking.
    """

    sql = ' DELETE FROM bookings WHERE id = ? '
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def delete_all_bookings(conn):
    """
    Delete all rows in bookings table.
    
    :param conn: connection to the SQLite database.
    """

    sql = 'DELETE FROM bookings'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def main():
    """
    Run the first time to set up SQLite Db file with table 'bookings' and columns.
    """

    ROOT_DIR = os.path.abspath('')
    config_path = '\\'.join([ROOT_DIR, 'config.json'])

    with open(config_path) as cfile:
        config = json.load(cfile)
        directories = config['directories']

    database = directories['db_file']

    sql_create_bookings_table = """ CREATE TABLE IF NOT EXISTS bookings (
                                        id integer PRIMARY KEY,
                                        ref text,
                                        equ text,
                                        nwt float,
                                        mrn text,
                                        pkg integer,
                                        abs text
                                    );"""

    # Create a database connection
    conn = create_connection(database)

    # Create table if database connection exists
    if conn is not None:
        create_table(conn, sql_create_bookings_table)
    else:
        print("Error! Cannot create the database connection.")
    

if __name__ == '__main__':
    main()