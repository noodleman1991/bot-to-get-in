from google.oauth2.service_account import Credentials
import gspread

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = Credentials.from_service_account_file(os.getenv('path2json'), scopes=SCOPES)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(os.getenv('SPREADSHEET_ID'))
e_worksheet = sh.worksheet(os.getenv('SHEET_NAME'))

