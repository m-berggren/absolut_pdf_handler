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
    Create_booking does several things:
        - If equ does not exist it creates a new row in Db and writes to log file.
        - If abs already exists it will skip all steps and not add to Db or log file.
        - If both equ and dat on same row exists it will increment values of nwt and pkg in Db and log file.

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    :param log_filename: logging name from 'config.json'.
    :return: booking id.
    """

    cur = conn.cursor()
    cur.execute("SELECT id FROM bookings WHERE equ = ?", (booking[1],))
    exists_equ = cur.fetchone()

    cur.execute("SELECT id FROM bookings WHERE abs = ?", (booking[5],))
    exists_abs = cur.fetchone()

    cur.execute("SELECT id FROM bookings WHERE equ = ? AND dat = ?", (booking[1], booking[6],))
    exists_ref_equ_dat = cur.fetchone()
    
    m = booking
    nl = "\n"
    nwt_upd, pkg_upd = "", ""
    nwt = f'{m[2]:5.2f}'.rjust(8)

    if exists_equ is None:
        sql = ''' INSERT INTO bookings(ref, equ, nwt, mrn, pkg, abs, dat)
                VALUES(?, ?, ?, ?, ?, ?, ?) '''
        cur.execute(sql, booking)
        conn.commit()
        debug_format = f'{"NEW:":>12}|{m[0]:^14}|{m[1]:^13}|{nwt:^10}|{m[3]:^20}|{m[4]:^6}|{m[5]:^10}|{m[6]:^12}'

    elif exists_abs:
        return

    elif exists_ref_equ_dat:
        info = update_booking_3_param(conn, booking)
        nwt_upd = f'{info["nwt"][0]:5.2f}'.rjust(8)
        pkg_upd = info["pkg"][0]

        debug_format = f'{"ADDED:":>12}|{m[0]:^14}|{m[1]:^13}|{nwt:^10}|{m[3]:^20}|{m[4]:^6}|{m[5]:^10}|{m[6]:^12}{nl}\
                        |{"NEW VALUES:":>13}|{" ":14}|{" ":13}|{nwt_upd:^10}|{" ":20}|{pkg_upd:^6}|{" ":10}|{ " ":12}'

    elif exists_equ:
        update_booking(conn, booking)
        debug_format = f'{"OVERWRITE:":>12}|{m[0]:^14}|{m[1]:^13}|{m[2]:^10}|{m[3]:^20}|{m[4]:^6}|{m[5]:^10}|{m[6]:^12}'

    else:
        return  

    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as f:
            f.write(f'{"DATE & TIME:":^24}|{"STATUS:":^13}|{"REF:":^14}|{"EQU:":^13}|{"NWT:":^10}|{"MRN:":^20}|{"PKG:":^6}|{"ABS:":^10}|{"DAT:":^12}{nl}')

    logging_file.debug_logger(debug_format, log_filename)

    return cur.lastrowid


def update_booking(conn, booking):
    """
    Update ref, nwt, mrn, pkg of a unit (equ).

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    """

    sql = ''' UPDATE bookings
                SET ref = ?,
                    nwt = ?,
                    mrn = ?,
                    pkg = ?,
                    abs = ?,
                    dat = ?
                WHERE equ = ? '''
    cur = conn.cursor()
    cur.execute(sql, booking)
    conn.commit()

def update_booking_3_param(conn, booking):
    """
    Similar to 'update booking'-function but if ref,
    equ and dat are found on the same row,
    it will increment nwt and pkg.

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    """

    sql = ''' UPDATE bookings
                SET ref = ?,
                    equ = ?,
                    nwt = nwt + ?,
                    mrn = ?,
                    pkg = pkg + ?,
                    abs = ?,
                    dat = ?
                WHERE ref = ? AND equ = ? AND dat = ?'''

    cur = conn.cursor()
    cur.execute(sql, (booking[0],
                        booking[1],
                        booking[2],
                        booking[3],
                        booking[4],
                        booking[5],
                        booking[6],
                        booking[0],
                        booking[1],
                        booking[6]))

    cur.execute("SELECT nwt FROM bookings WHERE equ = ? AND dat = ?", (booking[1], booking[6],))
    nwt = cur.fetchone()
    cur.execute("SELECT pkg FROM bookings WHERE equ = ? AND dat = ?", (booking[1], booking[6],))
    pkg = cur.fetchone()               
    conn.commit()

    return {"nwt": nwt, "pkg": pkg}

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
    
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except sqlite3.OperationalError as e:
        print("Error:", e)

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
                                        abs text,
                                        dat text
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