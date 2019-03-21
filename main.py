import csv
import gspread
import argparse
from oauth2client.service_account import ServiceAccountCredentials
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

GOOGLE_SCOPE = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']

parser = argparse.ArgumentParser(description='Update CSV to google sheets.')

parser.add_argument('update', help='update to sheet')
parser.add_argument('--history', help='update to history', action='store_true')
parser.add_argument('--date', help='day to scrape', type=str, default='')

args = vars(parser.parse_args())


class GoogleSheets:
    def __init__(self, cred_path='', scope=None):
        self.scope = scope
        self.cred_path = cred_path
        self.credentials = ''
        self.gc = None
        self.OSS = None
        self.wks = None

    def _get_credentials(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.cred_path, self.scope)

    def _get_access_gc(self):
        self.gc = gspread.authorize(self.credentials)

    def open_spread_sheet(self, key=''):
        self._get_credentials()
        self._get_access_gc()
        if key:
            self.OSS = self.gc.open_by_key(key=key)
            return self.OSS
        return self.OSS

    def open_work_sheet(self, name='', num=None):
        if name:
            self.wks = self.OSS.worksheet(name)
        elif num:
            self.wks = self.OSS.worksheet(num)
        else:
            self.wks = self.OSS.worksheet1
        return self.wks

    def reset_work_sheet(self, wks=None):
        if wks:
            wks.resize(rows=1)
        else:
            self.wks.resize(rows=1)


def _get_today_csv():
    with open('data/today.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            yield row


def update_today():
    ss.open_work_sheet('today')
    ss.reset_work_sheet()
    for row in _get_today_csv():
        ss.wks.append_row(row, value_input_option='USER_ENTERED')


def update_today_to_history():
    ss.open_work_sheet('history')
    for row in _get_today_csv():
        ss.wks.append_row(row, value_input_option='USER_ENTERED')


def start_crawling(date):
    process = CrawlerProcess(get_project_settings())
    process.crawl('w2', from_date=date)
    process.start()


if __name__ == '__main__':
    start_crawling(date=args['date'])
    ss = GoogleSheets(cred_path='sheets.json', scope=GOOGLE_SCOPE)
    ss.open_spread_sheet(key="1yyoZsuu8DFfjR-G_OXAasbMiBJNAIZIHyYusPrPUImQ")
    if args['update']:
        if args['history']:
            update_today_to_history()
        else:
            update_today()
