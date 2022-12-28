import csv
import json

import spacy
import xlrd
import xlwt
from spacy.matcher.phrasematcher import PhraseMatcher

from utils import get_spacy_document

matching_phrases_fieldnames = ['site_id', 'page_id', 'keyword_id', 'similar_kw_id', 'phrases_count']
matching_kw_fieldnames = ['site_id', 'page_id', 'keyword_id', 'similar_kw_id', 'page_keyword']
TEXTS_PRE_PROCESSED_XLSX = '../pre-processing/files/webPagesPreProcessedTexts.xls'
MATCHING_PHRASES_XLSX = 'files/matching_Phrases.xls'
SITE_COUNT = 1
PAGE_COUNT = 100000
START_PAGE_INDEX = 0

council_map = {}
with open('../crawler/italian/italian_council_map.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        council_map[row['id']] = row['council']

key_words_map = {}
#with open('keywords.csv', mode='r') as keywords_csv_file:
with open('italian/indexed_italian_keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_map[row['id']] = row['keyword']

similar_keywords_list = []

with open('italian/similar_italian_keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        similar_keywords_list.append(row)


def init_matching_phrases():
    with open('italian/matching_keyphrases_bari.csv', mode='w') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writeheader()


def write_matching_phrases(site_id, page_id, keyword_index_l, similar_kw_id_l, phrases_count):
    with open('italian/matching_keyphrases_bari.csv', mode='a') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writerow({'site_id': site_id,
                                                     'page_id': page_id,
                                                     'keyword_id': keyword_index_l,
                                                     'similar_kw_id': similar_kw_id_l,
                                                     'phrases_count': phrases_count})


def search_for_keyword(keyword_l, doc_obj, nlp_o):
    phrase_matcher = PhraseMatcher(nlp_o.vocab)
    phrase_list = [nlp_o(keyword_l)]
    phrase_matcher.add("Text Extractor", None, *phrase_list)

    matched_items = phrase_matcher(doc_obj)

    matched_text = []
    for match_id, start, end in matched_items:
        text = nlp_o.vocab.strings[match_id]
        span = doc_obj[start: end]
        matched_text.append(span.sent.text)

    return matched_text


def search_web_page_texts():
    print("Searching Web page texts")
    f = open('../../italian-configs.json')
    config = json.load(f)
    init_matching_phrases()
    wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
    wb_w_y = xlwt.Workbook()
    # nlp.add_pipe('setCustomBoundaries', before='parser')
    site = 0
    config['sites'] = [{
        "name": "Bari council",
        "folder": "bari"
    }]
    for j in config['sites']:
        print(j['name'])
        sheet = wb.sheet_by_index(site)
        print(sheet.name)
        index = START_PAGE_INDEX
        site_urls = []
        council_index = -1
        with open("../crawler/files/italy/" + j['folder'] + "/site_urls.csv") as urls_file:
            urls_file_reader = csv.DictReader(urls_file)
            for row_l in urls_file_reader:
                site_urls.append(row_l)
                council_index = row_l['council']
        max_count = min(PAGE_COUNT, len(site_urls))
        sheet_w = wb_w_y.add_sheet(council_map[str(council_index)])
        sheet_w.write(0, 1, 'site_id')
        sheet_w.write(0, 2, 'page_id')
        sheet_w.write(0, 3, 'key_word_id')
        sheet_w.write(0, 4, 'key_word')
        sheet_w.write(0, 5, 'similar_word')
        sheet_w.write(0, 6, 'phrase')
        sheet_w.write(0, 0, 'id')
        row_id = 1
        for keyword in similar_keywords_list:
            count = 1
            for i in range(0, max_count):
                # spacy_obj = get_spacy_document(str(sheet.cell_value(i, 0)), nlp)
                # matching_phrases = search_for_keyword(keyword['similar_keyword'], spacy_obj, nlp)
                # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                # if len(matching_phrases) > 0:
                if len(str(keyword).split(' ')) < 2:
                    words = str(sheet.cell_value(i, 0)).split(' ')
                    for word in words:
                        if str(word) == keyword['similar_keyword']:
                            write_matching_phrases(council_index, str(council_index) + '_' + str(count), keyword['keyword_id'],
                                                   keyword['id'], 1)
                else:
                    try:
                        if str(sheet.cell_value(i, 0)).__contains__(keyword['similar_keyword']):
                            write_matching_phrases(council_index, str(council_index) + '_' + str(count), keyword['keyword_id'],
                                                keyword['id'], 1)
                    except:
                        print()
                    # sheet_w.write(row_id, 1, site)
                    # sheet_w.write(row_id, 2, str(site) + '_' + str(count))
                    # sheet_w.write(row_id, 3, keyword['keyword_id'])
                    # sheet_w.write(row_id, 4, key_words_map[keyword['keyword_id']])
                    # sheet_w.write(row_id, 5, keyword['similar_keyword'])
                    # sheet_w.write(row_id, 6, str(sheet.cell_value(i, 0)))
                    # sheet_w.write(row_id, 0, row_id)
                    # row_id = row_id + 1
                count = count + 1

                print('Page : ' + str(count))
            print('Keyword : ' + keyword['similar_keyword'] + '  -  ' + str(keyword['id']))
        site = site + 1
    wb_w_y.save('%s' % MATCHING_PHRASES_XLSX)


if __name__ == '__main__':
    search_web_page_texts()
