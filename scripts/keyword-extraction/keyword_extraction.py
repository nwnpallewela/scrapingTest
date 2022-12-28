import csv
import json

import xlrd

from scripts.utils.progress_bar import print_progress_bar
from yake import yake

TEXTS_PRE_PROCESSED_XLSX = "../pre-processing/files/webPagesPreProcessedTexts.xls"
SITE_COUNT = 5
PAGE_COUNT = 19990
START_PAGE_INDEX = 0

if __name__ == '__main__':
    f = open('../../configs.json')
    config = json.load(f)
    if config.get('enableYake'):
        kw_extractor = yake.KeywordExtractor()
        wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
        with open('files/yake_key_words.csv', mode='w') as yake_key_words:
            fieldnames = ['Site', 'Page', 'KeyWord', 'Value']
            key_words_writer = csv.DictWriter(yake_key_words, fieldnames=fieldnames)
            key_words_writer.writeheader()
            site = 0
            sheet_count = 0
            for j in config['sites']:
                print(j['name'])
                index = START_PAGE_INDEX
                site_urls = []
                with open("../crawler/files/" + j['folder'] + "/site_urls.csv") as urls_file:
                    urls_file_reader = csv.DictReader(urls_file)
                    for row in urls_file_reader:
                        site_urls.append(row)
                max_count = min(PAGE_COUNT, len(site_urls))
                sheet = wb.sheet_by_index(sheet_count)
                print(sheet.name)
                count = 1
                row = 1
                for i in range(0, max_count):
                    keywords = kw_extractor.extract_keywords(str(sheet.cell_value(i, 0)))
                    print_progress_bar(i, max_count, prefix='Extract Web Page Text    :',
                                       suffix='Complete',
                                       length=50)
                    for word in keywords:
                        key_words_writer.writerow({'Site': site, 'Page': str(site) + '_' + str(count)
                                                      , 'KeyWord': word[0], 'Value': word[1]})
                        row = row + 1
                    count = count + 1
                site = site + 1
                sheet_count = sheet_count + 1
