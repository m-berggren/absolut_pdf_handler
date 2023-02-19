from datetime import datetime
import json
import logging
import os
from tqdm import tqdm
import win32com.client

ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']
    outlook = config['outlook']

logger4 = logging.getLogger('outlook_debug')
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

def download_pdfs_in_folder():
    """
    Loops through all e-mails in a certain folder and downloads
    all PDF attachments locally, then moves that file in Outlook
    to a new folder.
    """

    out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')
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