from __future__ import print_function

import argparse
from google.cloud import language

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()

def sentiment_text(text):
    """Detects sentiment in the text."""
    language_client = language.Client()

    # Instantiates a plain text document.
    document = language_client.document_from_text(text)

    # Detects sentiment in the document. You can also analyze HTML with:
    #   document.doc_type == language.Document.HTML
    sentiment = document.analyze_sentiment()
    return sentiment.score

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.
        
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        
        Returns:
        Credentials, the obtained credential.
        """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.
        
        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    
    spreadsheetId = '1t93ixnRBnAW5qhYHil6oE2jwK0xF31Q51Cq42OJ0lsw'
    rangeName = 'A:D'
    result = service.spreadsheets().values().get( spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
    else:
        pos_dict = { }
        neg_dict = { }
        net_dict = { }
        count_dict = { }
        #pos_sent, neg_sent = 0, 0
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            try:
                neg_review = row[0]
                pos_review = row[3]
                name = row[2]
                if name not in net_dict.keys():
                    net_dict[name] = 0
                    count_dict[name] = 0
                    pos_dict[name] = 0
                    neg_dict[name] = 0
                count_dict[name] += 1
                pos_sent = sentiment_text(pos_review)
                neg_sent = sentiment_text(neg_review)
                pos_dict[name] += pos_sent
                neg_dict[name] += neg_sent
                net_dict[name] += pos_sent + neg_sent
            except IndexError:
                print(row)
        for name in count_dict:
            pos_dict[name] = pos_dict[name]/count_dict[name]
            neg_dict[name] = neg_dict[name]/count_dict[name]
            net_dict[name] = net_dict[name]/count_dict[name]

        print("Pos dict", pos_dict, '\n')
        print("Neg dict", neg_dict, '\n')
        print("Net dict", net_dict, '\n')

if __name__ == '__main__':
    main()



