import win32com.client
import os
import json


ROOT_DIR = os.path.abspath('')
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as cfile:
    config = json.load(cfile)
    directories = config['directories']
    outlook = config['outlook']

EMAIL_ACCOUNT = outlook['email']
FOLDER1 = outlook['folder1']
FOLDER2 = outlook['folder2']
FOLDER3 = outlook['folder3']
FOLDER4 = outlook['folder4']
FOLDER5 = outlook['folder5']
TO_FOLDER = outlook['move_to_folder']
SAVE_AS_PATH = directories['outl_save_dir']

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

    mail_count = iter_folder.Items.Count

    if mail_count > 0:

        for i in range(mail_count, 0, -1):
            mail = iter_folder.Items[i]

            if '_MailItem' in str(type(mail)):
                print(type(mail))

                if mail.Attachments.Count > 0:

                    for attachment in mail.Attachments:
                        attachment.SaveAsFile(os.path.join(SAVE_AS_PATH, attachment.FileName))
                        try:
                            mail.Move(move_to_folder)
                        except Exception:
                            print(f"Cannot move file to {TO_FOLDER}")
                else: continue

    else:
        print(f"No items found in: {FOLDER5}")

if __name__ == '__main__':
    download_pdfs_in_folder()