import csv
import json
from xlutils.copy import copy
import pandas as pd
import xlrd
import xlwt
from nltk.corpus import stopwords

from scripts.utils.progress_bar import print_progress_bar

WEB_PAGE_TEXTS_XLSX = "../text-extractor/files/webPagesExtractedTexts.xls"
WEB_PAGE_TEXTS_XLSX_PREFIX = "../text-extractor/files/webPagesExtractedTexts_"
WEB_PAGE_TEXTS_XLSX_POSTFIX = ".xlsx"
TEXTS_PRE_PROCESSED_XLSX = "files/webPagesPreProcessedTexts.xls"
SITE_COUNT = 1
PAGE_COUNT = 500000

if __name__ == '__main__':
    f = open('../../configs.json')
    config = json.load(f)
    stop = stopwords.words('english')
    # wb = xlrd.open_workbook('%s' % WEB_PAGE_TEXTS_XLSX)
    rb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
    wb_w = copy(rb)
    for i in config['sites']:
        if i.get('actions').get('preprocess_text') != 'completed':
            site_urls = []
            with open("../crawler/files/" + i['parent_folder'] + "/" + i['folder'] + "/site_urls.csv") as urls_file:
                urls_file_reader = csv.DictReader(urls_file)
                for row in urls_file_reader:
                    site_urls.append(row)
            max_count = min(PAGE_COUNT, len(site_urls))
            # df_l = pd.read_excel(WEB_PAGE_TEXTS_XLSX, sheet_name=i['folder'])
            wb = xlrd.open_workbook('%s' % (WEB_PAGE_TEXTS_XLSX_PREFIX + i['folder'] + WEB_PAGE_TEXTS_XLSX_POSTFIX))
            sheet = wb.sheet_by_name(i['folder'])
            sheet_new = wb_w.add_sheet(i['folder'])
            for i_1 in range(0, max_count):
                try:
                    val = str(sheet.cell_value(i_1, 3)).lower().replace('[^/w/s]', '')
                    val = ' '.join(x for x in val.split() if x not in stop)
                    sheet_new.write(i_1, 0, val)
                except:
                    print("Error extracting text")

            # df_n = pd.DataFrame(data=preprocessed_texts)
    try:
        wb_w.save(TEXTS_PRE_PROCESSED_XLSX)
    except:
        print()

    print("Done!!")
