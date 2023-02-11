import json
import os

import fitz

import logging_file

def pdf_parser(pdf):
    """
    Goes through a PDF file and gather below data in two steps:

        1)  Loop through all pages, adding info for each word and rectangle
            coordinates (x0, y0, x1, y1) to a list with incremented y-values.

        2)  In this loop 6 key words/sentences are searched (REF, PKG, NWT, EQU, MRN, ABS)
            to find the corresponding positions. These are used in a list comprehension
            where rectangles intersect.

    Gathered data:
        - MLO booking ref (ref)
        - Container number (equ)
        - Net weight (nwt)
        - Movement Reference Number (mrn)
        - Packages (pgk)
        - Ref from Absolut (abs)

    :param pdf: pdf file to iterate through.
    """

    REF = "Booking No."
    PKG = "Sum:"
    NWT = "Total gross weight to be used in BL"
    EQU = "CONT:"
    MRN = "MRN no:"
    ABS = "Reference No."

    ROOT_DIR = os.path.abspath('')
    config_path = '\\'.join([ROOT_DIR, 'config.json'])

    with open(config_path) as cfile:
        config = json.load(cfile)
        directories = config['directories']

    PDF_DIR = directories['pdf_dir']
    file_path = '\\'.join([ROOT_DIR, PDF_DIR, pdf])

    # Read pdf file
    with open(file_path) as fp:
        doc = fitz.open(fp)

    def alter_values(val, const_val):
        """
        Function to determine if a word exist on page,
        if not it adds to total height on y-values.

        :param val: stored value, rectangle coordinates.
        :param const_val: keyword from 'config.json'.
        :return: rectangle coordinates (x0, y0, x1, y1).
        """

        if not val:
            val = page.search_for(const_val)
            try:
                val = val[0]
                val += (0, total_height, 0, total_height)
            except:
                pass
        return val

    """
    Main loop with variables below:
    """

    total_height = 0.0
    total_words = []
    ref, pkg, nwt, equ, mrn, abs = "", "", "", "", "", ""

    for page in doc:
        word_list = page.get_text("words")
        for w in word_list:
            total_words.append([w[0], w[1] + total_height, w[2], w[3] + total_height, w[4]])

        ref = alter_values(ref, REF)
        pkg = alter_values(pkg, PKG)
        nwt = alter_values(nwt, NWT)
        equ = alter_values(equ, EQU)
        mrn = alter_values(mrn, MRN)
        abs = alter_values(abs, ABS)
        
        total_height += page.rect.height

    # Adjust rectangles to get the correct return value/word.
    try:
        ref = ref + (0, 9, 40, 13)
    except TypeError as error:
        print(error)

    try:
        pkg = pkg + (204, 0, 230, 0)
    except TypeError as error:
        print(error)

    try:
        nwt = nwt + (300, 0, 261, 0)
    except TypeError as error:
        print(error)

    try:
        equ = equ + (42, 0, 84, 0)
    except TypeError as error:
        print(error)

    try:
        mrn = mrn + (48, 0, 114, 0)
    except TypeError as error:
        print(error)

    try:
        abs = abs + (0, 8, 0, 13)
    except TypeError as error:
        print(error)

    def get_word_in_rect(rect):
        """ 
        List comprehension that gets the intersection of two rectangles.
        
        :param rect: rectangle values.
        :return: word found where rectangles intersect or nothing if error.
        """
    
        try:
            return [word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)][0]
        except ValueError as error:
            return ""

    try:
        ref = get_word_in_rect(ref)
    except (IndexError, TypeError) as error:
        ref = ""

    try:
        pkg = int(get_word_in_rect(pkg))
    except (IndexError, TypeError) as error:
        pkg = 0

    try:
        nwt = float(get_word_in_rect(nwt).replace(",", "."))
    except (IndexError, TypeError) as error:
        nwt = 0.0

    try:
        equ = get_word_in_rect(equ)
        if len(equ) < 11:
            equ = ""
    except (IndexError, TypeError) as error:
        equ = ""

    try:
        mrn = get_word_in_rect(mrn)
    except (IndexError, TypeError) as error:
        mrn = ""

    try:
        abs = get_word_in_rect(abs)
    except (IndexError, TypeError) as error:
        abs = ""

    booking_dict = {
            'ref': ref,
            'equ': equ,
            'nwt': nwt,
            'mrn': mrn,
            'pkg': pkg,
            'abs': abs
            }

    return booking_dict

    
def create_booking(pdf_name, cfg_log_filename):
    """
    Calls the pdf_parser() function, return data in tuple for SQLite Db.
    Also writes all data to a log file.
    
    :param pdf_name: name of the PDF file to be used.
    :param cfg_log_filename: logging name from 'config.json'.
    :return: (ref, equ, nwt, mrn, pkg, abs) returned in a tuple.
    """

    m = pdf_parser(pdf_name)
    data = (m['ref'], m['equ'], m['nwt'], m['mrn'], m['pkg'], m['abs'])
    logging_file.debug_logger(data, cfg_log_filename)

    return data


def update_booking(pdf_name, cfg_log_filename):
    """ 
    Almost identical to 'create booking'-function, the returned tuple is instead:
    
    :param pdf_name: name of the PDF file to be used.
    :param cfg_log_filename: logging name from 'config.json'.
    :return: (ref, equ, nwt, mrn, pkg, abs, equ) returned in a tuple.
    """
    m = pdf_parser(pdf_name)
    data = (m['ref'], m['nwt'], m['mrn'], m['pkg'], m['abs'], m['equ'])
    logging_file.debug_logger(data, cfg_log_filename)

    return data

if __name__ == '__main__':
    #print(pdf_parser(r'(1) 51062492_149033S.pdf')) #file is faulty, missing ref. Good practise example.
    print(pdf_parser(r'(1) 51063742_147126S.pdf')) #file is faulty, missing mrn. Good practise example.

    