import json
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
        - MLO booking reference (reference)
        - Container number (container)
        - Net weight (net_weight)
        - Movement Reference Number (mrn_number)
        - Packages (pgk)
        - Ref from Absolut (absolut)

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

    pdf_dir = config['directories']['pdf_dir']
    file_path = '\\'.join([ROOT_DIR, pdf_dir, pdf])


    # Read pdf file
    with open(file_path) as f:
        doc = fitz.open(f)

    def search_string_and_alter_rectangle(variable, rectangle, match):
        """
        Function to determine if a word exist on page,
        if not it adds to total height on y-values.

        :param val: stored value, rectangle coordinates.
        :param const_val: keyword from 'config.json'.
        :return: rectangle coordinates (x0, y0, x1, y1).
        """

        if not variable:
            variable = page.search_for(match)
            if variable:
                variable = variable[0]
                variable += (0, total_height, 0, total_height)
                variable += rectangle
                return variable
        return variable

    """
    Main loop with variables below:
    """

    total_height = 0.0
    total_words = []
    reference, package, net_weight, container, mrn_number, absolut, date_sent = "", 0, 0.0, "", "", "", ""

    ref_rect = (0, 9, 40, 13)
    pkg_rect = (204, 0, 230, 0)
    nwt_rect = (300, 0, 261, 0)
    equ_rect = (42, 0, 84, 0)
    mrn_rect = (48, 0, 114, 0)
    abs_rect = (0, 8, 0, 13)
    dat_rect = (192, 9, 206, 13)

    for page in doc:
        word_list = page.get_text("words")
        for w in word_list:
            total_words.append([w[0], w[1] + total_height, w[2], w[3] + total_height, w[4]])

        reference = search_string_and_alter_rectangle(reference, ref_rect, REF)
        package = search_string_and_alter_rectangle(package, pkg_rect, PKG)
        net_weight = search_string_and_alter_rectangle(net_weight, nwt_rect, NWT)
        container = search_string_and_alter_rectangle(container, equ_rect, EQU)
        mrn_number = search_string_and_alter_rectangle(mrn_number, mrn_rect, MRN)
        absolut = search_string_and_alter_rectangle(absolut, abs_rect, ABS)
        date_sent = search_string_and_alter_rectangle(date_sent, dat_rect, DAT)
        
        total_height += page.rect.height


    def get_word_in_rect(rect):
        """ 
        List comprehension that gets the intersection of two rectangles.
        
        :param rect: rectangle values.
        :return: word found where rectangles intersect or nothing if error.
        """

        if rect:
            try:
                return [word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect) and rect][0]
            except (ValueError, IndexError):
                return ""

            
    reference = get_word_in_rect(reference)
    package = get_word_in_rect(package)
    net_weight = get_word_in_rect(net_weight)
    container = get_word_in_rect(container)
    mrn_number = get_word_in_rect(mrn_number)
    absolut = get_word_in_rect(absolut)
    date_sent = get_word_in_rect(date_sent)

    if not reference: reference = ""
    if package:
        package = int(package)
    else: package = 0

    if net_weight:
        net_weight = float(net_weight.replace(",", "."))
    else: net_weight = 0.0

    if container:
        if len(container) < 11:
            container = ""
    else: container = ""
    
    if not mrn_number: mrn_number = ""
    if not absolut: absolut = ""
    if not date_sent: date_sent = ""
    

    booking_dict = {
            'reference': reference,
            'container': container,
            'net_weight': net_weight,
            'mrn_number': mrn_number,
            'package': package,
            'absolut': absolut,
            'date_sent': date_sent
            }

    return booking_dict

    
def create_booking(pdf_name):
    """
    Calls the pdf_parser() function, return data in tuple for SQLite Db.
    
    :param pdf_name: name of the PDF file to be used.
    :return: (reference, container, net_weight, mrn_number, package, absolut, date_sent) returned in a tuple.
    """

    m = pdf_parser(pdf_name)
    data = (m['reference'], m['container'], m['net_weight'], m['mrn_number'], m['package'], m['absolut'], m['date_sent'])

    return data


if __name__ == '__main__':
    print(pdf_parser(r'(1) 51067152_149428S.pdf')) 

    