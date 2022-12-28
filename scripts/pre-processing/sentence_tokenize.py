import csv
import json

import xlrd
from scripts.utils.progress_bar import print_progress_bar
import nltk
from nltk import sent_tokenize

nltk.download('punkt')

TEXTS_PRE_PROCESSED_XLSX = "../pre-processing/files/webPagesPreProcessedTexts.xls"
SITE_COUNT = 5
PAGE_COUNT = 19990
START_PAGE_INDEX = 0

if __name__ == '__main__':
    f = open('../../configs.json')
    config = json.load(f)
    wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
    with open('files/web_pages_text_sent_token.csv', mode='w') as web_pages_text_sent_token:
        fieldnames = ['site', 'page', 'sent', 'text']
        web_pages_text_sent_token_writer = csv.DictWriter(web_pages_text_sent_token, fieldnames=fieldnames)
        web_pages_text_sent_token_writer.writeheader()
        site = 0
        sheet_count = 0
        for j in config['sites']:
            if j['folder'] == 'melbourne':
                site = 0
            elif j['folder'] == 'act':
                site = 1
            elif j['folder'] == 'ryde':
                site = 3
            elif j['folder'] == 'sydney':
                site = 2
            elif j['folder'] == 'brisbane':
                site = 4

            print(j['name'] + '' + str(site))
            index = START_PAGE_INDEX
            site_urls = []
            with open("../crawler/files/" + j['folder'] + "/site_urls.csv") as urls_file:
                urls_file_reader = csv.DictReader(urls_file)
                for row in urls_file_reader:
                    site_urls.append(row)
            max_count = min(PAGE_COUNT, len(site_urls))
            sheet = wb.sheet_by_index(sheet_count)
            print(sheet.name)
            count = 0
            for i in range(index, max_count):
                sentences = sent_tokenize(str(sheet.cell_value(i, 0)))
                print_progress_bar(i - START_PAGE_INDEX, max_count - START_PAGE_INDEX, prefix='Tokenize Web Page Text:',
                                   suffix='Complete',
                                   length=50)
                for sentence in sentences:
                    web_pages_text_sent_token_writer.writerow({'site': site, 'page': str(site) + '_' + str(i + 1),
                                                               'sent': str(site) + '_' + str(count), 'text': sentence})
                    count = count + 1
            sheet_count = sheet_count + 1
