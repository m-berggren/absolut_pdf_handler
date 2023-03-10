import json
import logging
import os
from tqdm import tqdm
import win32com.client
import win32com
import win32ui
from pathlib import Path

ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']
    outlook = config['outlook']

logger4 = logging.getLogger(__name__)
logger4.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
file_handler = logging.FileHandler(directories['debug_outlook_dl'])
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger4.addHandler(file_handler)

EMAIL_ACCOUNT = outlook['email']
FOLDER1 = outlook['folder1']
FOLDER2 = outlook['folder2']
FOLDER3 = outlook['folder3']
FOLDER4 = outlook['folder4']
FOLDER5 = outlook['folder5']
TO_FOLDER = outlook['move_to_folder']
PDF_DIR = directories['pdf_dir'].replace("/", "\\")

def outlook_window_exists():
    try:
        win32ui.FindWindow(None, "Microsoft Outlook")
        return True
    except win32ui.error:
        return False

def download_pdfs_in_folder():
    """
    Loops through all e-mails in a certain folder and downloads
    all PDF attachments locally, then moves that file in Outlook
    to a new folder.
    """

    """Creates error sometimes - then needed to remove $USERNAME$\AppData\Local\Temp\gen_py folder.
    New solution is to change 'gen_py' folder so it does not clash with other processes.
    """

    if win32com.client.gencache.is_readonly == True:
    
        #allow gencache to create the cached wrapper objects
        win32com.client.gencache.is_readonly = False
    
        # under p2exe the call in gencache to __init__() does not happen
        # so we use Rebuild() to force the creation of the gen_py folder
        win32com.client.gencache.Rebuild()
    
        # NB You must ensure that the python...\win32com.client.gen_py dir does not exist
        # to allow creation of the cache in %temp%

    """Issues for some users with below 4 lines"""

    try:
        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')
    except:
        home = str(Path.home())
        gen_py_path = os.path.join(home, r"AppData\Local\gen_py\3.10")
        Path(gen_py_path).mkdir(parents=True, exist_ok=True)
        win32com.__gen_path__ = gen_py_path
        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')

    """"""

    if not outlook_window_exists():
        print("Outlook is not running, please start application and run this file again to download files.")
        exit()

    mapi = out_app.GetNamespace('MAPI')

    iter_folder = mapi.Folders[EMAIL_ACCOUNT].Folders[FOLDER1].Folders[FOLDER2].Folders[FOLDER3].Folders[FOLDER4].Folders[FOLDER5]
    move_to_folder = iter_folder.Folders[TO_FOLDER]

    save_as_path = os.path.join(ROOT_DIR, PDF_DIR)

    mail_count = iter_folder.Items.Count

    if mail_count > 0:

        for i in tqdm(range(mail_count, 0, -1), desc='E-mail download counter', unit='E-mails'):
            mail = iter_folder.Items[i]
            
            if '_MailItem' in str(type(mail)):
                
                if mail.Attachments.Count > 0:
                    for attachment in mail.Attachments:
                        if attachment.FileName.startswith('(1)'):
                            attachment.SaveAsFile(os.path.join(save_as_path, attachment.FileName))
                            logger4.info(f'Attachment {attachment.FileName} saved to {PDF_DIR}.')

                            mail.UnRead = False

                            try:
                                mail.Move(move_to_folder)
                            except Exception:
                                logger4.debug("Cannot move email with attachment {attachment.FileName} to {TO_FOLDER}")

    else:
        logger4.debug(f"No items found in: {FOLDER5}")

if __name__ == '__main__':
    download_pdfs_in_folder()