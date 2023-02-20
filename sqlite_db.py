import json
import logging
import os
import sqlite3

ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']

database = directories['db_file']


logger1 = logging.getLogger(__name__)
logger1.setLevel(logging.DEBUG)
formatter1 = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
file_handler1 = logging.FileHandler(directories['debug_sqlite_db'])
file_handler1.setLevel(logging.DEBUG)
file_handler1.setFormatter(formatter1)
logger1.addHandler(file_handler1)

logger2 = logging.getLogger('bookings_log')
logger2.setLevel(logging.INFO)
formatter2 = logging.Formatter('%(asctime)s | %(message)s')
file_handler2 = logging.FileHandler(directories['bookings_log'])
file_handler2.setLevel(logging.INFO)
file_handler2.setFormatter(formatter2)
logger2.addHandler(file_handler2)

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
        logger1.debug(e)
    
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
        logger1.debug(e)

def execute_sqlite(conn, booking):
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

    cur.execute("SELECT id FROM bookings WHERE instr(abs, ?) > 0", (booking[5],))
    exists_abs = cur.fetchone()
    
    cur.execute("SELECT id FROM bookings WHERE equ = ? AND dat = ?", (booking[1], booking[6],))
    exists_equ_dat = cur.fetchone()

    cur.execute("SELECT id FROM bookings WHERE equ = ? AND dat < ?", (booking[1], booking[6],))
    equ_exists_and_dat_later = cur.fetchone()


    m = booking
    nl = "\n"
    nwt_upd, pkg_upd = "", ""
    nwt = f'{m[2]:5.2f}'.rjust(8)
    booking_log_format = ""

    if exists_equ is None:
        create_booking(conn, booking)
        booking_log_format =  f'{"NEW:":>12}|{m[0]:^14}|{m[1]:^13}|{nwt:^10}|{m[3]:^20}|{m[4]:^6}|{m[6]:^12}|{m[5]}'

    elif exists_abs:
        return

    elif exists_equ_dat:
        info = update_booking_3_param(conn, booking)
        nwt_upd = f'{info[3]:5.2f}'.rjust(8)

        booking_log_format = f'{"ADDED:":>12}|{m[0]:^14}|{m[1]:^13}|{nwt:^10}|{m[3]:^20}|{m[4]:^6}|{m[6]:^12}|{m[5]}{nl}\
                        |{"NEW VALUES:":>13}|{" ":14}|{" ":13}|{nwt_upd:^10}|{" ":20}|{info[5]:^6}|{ " ":12}|{info[6]}'

    elif equ_exists_and_dat_later:
        upd = update_booking(conn, booking)
        booking_log_format = f'{"OVERWRITE:":>12}|{upd[1]:^14}|{upd[2]:^13}|{upd[3]:^10}|{upd[4]:^20}|{upd[5]:^6}|{upd[7]:^12}|{upd[6]}'
        
    elif exists_equ:
        booking_log_format= f'Found {exists_equ} but all information already exists.'
    
    else:
        return
        

    logger2.info(booking_log_format)
        

def create_booking(conn, booking):
    """
    Creates ref, equ, nwt, mrn, pkg, abs and dat of a unit (equ).

    :param conn: connection to SQLite database.
    :param booking: data from 'pdf parser.py'.
    """

    sql = ''' INSERT INTO bookings(ref, equ, nwt, mrn, pkg, abs, dat)
                VALUES(?, ?, ?, ?, ?, ?, ?) '''
    
    cur = conn.cursor()
    cur.execute(sql, booking)
    conn.commit()


def update_booking(conn, booking):
    """
    Update ref, nwt, mrn, pkg of a unit (equ).

    :param conn: connection to the SQLite database.
    :param booking: data from 'pdf_parser.py'.
    """
    cur = conn.cursor()
    sql = ''' UPDATE bookings
                SET ref = ?,
                    nwt = ?,
                    mrn = ?,
                    pkg = ?,
                    abs = abs || ", " || ?,
                    dat = ?
                WHERE equ = ? AND dat < ? '''
    
    cur.execute(sql, (booking[0],
                        booking[2],
                        booking[3],
                        booking[4],
                        booking[5],
                        booking[6],
                        booking[1],
                        booking[6]))
    cur.execute("SELECT * FROM bookings WHERE equ = ?", (booking[1],))
    records = cur.fetchone()
    conn.commit()

    return records

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
                    nwt = nwt + ?,
                    mrn = ?,
                    pkg = pkg + ?,
                    abs = abs || ", " || ?,
                    dat = ?
                WHERE equ = ? AND dat = ?'''

    cur = conn.cursor()
    cur.execute(sql, (booking[0],
                        booking[2],
                        booking[3],
                        booking[4],
                        booking[5],
                        booking[6],
                        booking[1],
                        booking[6],))

    cur.execute("SELECT * FROM bookings WHERE equ = ? AND dat = ?", (booking[1], booking[6],))
    records = cur.fetchone()               
    conn.commit()

    return records

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
        logger1.debug(e)

def main():
    """
    Run the first time to set up SQLite Db file with table 'bookings' and columns.
    """

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
        logger1.debug("Error! Cannot create the database connection.")
    

if __name__ == '__main__':
    main()