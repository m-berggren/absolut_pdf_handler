import json
import logging
import os

import fitz

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
    DAT = "Place and date"

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
            except (TypeError, IndexError) as e:
                ""
    
        return val

    """
    Main loop with variables below:
    """

    total_height = 0.0
    total_words = []
    ref, pkg, nwt, equ, mrn, abs, dat = "", 0, 0.0, "", "", "", ""

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
        dat = alter_values(dat, DAT)
        
        total_height += page.rect.height

    # Adjust rectangles to get the correct return value/word.
    try:
        ref = ref + (0, 9, 40, 13)
    except TypeError as e:
        ""

    try:
        pkg = pkg + (204, 0, 230, 0)
    except TypeError as e:
        ""

    try:
        nwt = nwt + (300, 0, 261, 0)
    except TypeError as e:
        ""

    try:
        equ = equ + (42, 0, 84, 0)
    except TypeError as e:
        ""

    try:
        mrn = mrn + (48, 0, 114, 0)
    except TypeError as e:
        ""

    try:
        abs = abs + (0, 8, 0, 13)
    except TypeError as e:
        ""

    try:
        dat = dat + (192, 9, 206, 13)
    except TypeError:
        ""

    def get_word_in_rect(rect):
        """ 
        List comprehension that gets the intersection of two rectangles.
        
        :param rect: rectangle values.
        :return: word found where rectangles intersect or nothing if error.
        """
    
        try:
            return [word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)][0]
        except ValueError:
            return ""
            
    try:
        ref = get_word_in_rect(ref)
    except (IndexError, TypeError) as e:
        ref = ""

    try:
        pkg = int(get_word_in_rect(pkg))
    except (IndexError, TypeError) as e:
        pkg = 0

    try:
        nwt = float(get_word_in_rect(nwt).replace(",", "."))
    except (IndexError, TypeError, ValueError) as e:
        nwt = 0.0

    try:
        equ = get_word_in_rect(equ)
        if len(equ) < 11:
            equ = ""
    except (IndexError, TypeError) as e:
        equ = ""

    try:
        mrn = get_word_in_rect(mrn)
    except (IndexError, TypeError) as e:
        mrn = ""

    try:
        abs = get_word_in_rect(abs)
    except (IndexError, TypeError) as e:
        abs = ""

    try:
        dat = get_word_in_rect(dat)
    except (IndexError, TypeError) as e:
        dat = ""

    booking_dict = {
            'ref': ref,
            'equ': equ,
            'nwt': nwt,
            'mrn': mrn,
            'pkg': pkg,
            'abs': abs,
            'dat': dat
            }

    return booking_dict

    
def create_booking(pdf_name):
    """
    Calls the pdf_parser() function, return data in tuple for SQLite Db.
    
    :param pdf_name: name of the PDF file to be used.
    :return: (ref, equ, nwt, mrn, pkg, abs, dat) returned in a tuple.
    """

    m = pdf_parser(pdf_name)
    data = (m['ref'], m['equ'], m['nwt'], m['mrn'], m['pkg'], m['abs'], m['dat'])

    return data


if __name__ == '__main__':
    #print(pdf_parser(r'(1) 51062492_149033S.pdf')) #file is faulty, missing ref. Good practise example.
    print(pdf_parser(r'(1) 51060056_146897S.pdf')) 

    