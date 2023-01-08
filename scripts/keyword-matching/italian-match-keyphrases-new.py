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
PAGE_COUNT = 1000000
START_PAGE_INDEX = 0

council_map = {}
with open('../crawler/files/council_map.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        council_map[row['id']] = row['council']

italian_key_words_map = {}
# with open('keywords.csv', mode='r') as keywords_csv_file:
with open('italian/indexed_italian_keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        italian_key_words_map[row['id']] = row['keyword']

key_words_map = {}
# with open('keywords.csv', mode='r') as keywords_csv_file:
with open('files/keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_map[row['id']] = row['keyword']

italian_similar_keywords_list = []

with open('italian/similar_italian_keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        italian_similar_keywords_list.append(row)

similar_keywords_list = []
with open('files/similar_keyphrases.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        similar_keywords_list.append(row)


def init_matching_phrases():
    with open('files/matching_keyphrases_new.csv', mode='w') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writeheader()


def write_matching_phrases(site_id, page_id, keyword_index_l, similar_kw_id_l, phrases_count):
    with open('files/matching_keyphrases_new.csv', mode='a') as matching_phrases_csv_file_l:
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
    f = open('../../configs.json')
    config = json.load(f)
    for i in config['sites']:
        if i.get('actions').get('match_key_phrases') != 'completed':
            wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
            sheet = wb.sheet_by_name(i['folder'])
            index = START_PAGE_INDEX
            site_urls = []
            council_index = -1
            if i['parent_folder'] == 'aus':
                similar_keywords_list_l = similar_keywords_list
            else:
                similar_keywords_list_l = italian_similar_keywords_list
            with open("../crawler/files/" + i['parent_folder'] + "/" + i['folder'] + "/site_urls.csv") as urls_file:
                urls_file_reader = csv.DictReader(urls_file)
                for row_l in urls_file_reader:
                    site_urls.append(row_l)
                    council_index = row_l['council']
            max_count = min(PAGE_COUNT, len(site_urls))
            for keyword in similar_keywords_list_l:
                count = 1
                for j in range(0, max_count):
                    if len(str(keyword).split(' ')) < 2:
                        words = str(sheet.cell_value(j, 0)).split(' ')
                        for word in words:
                            if str(word) == keyword['similar_keyword']:
                                write_matching_phrases(council_index, str(council_index) + '_' + str(count),
                                                       keyword['keyword_id'], keyword['id'], 1)
                    else:
                        try:
                            if str(sheet.cell_value(j, 0)).__contains__(keyword['similar_keyword']):
                                write_matching_phrases(council_index, str(council_index) + '_' + str(count),
                                                           keyword['keyword_id'], keyword['id'], 1)
                        except:
                            print()
                    count = count + 1
                    print('Page : ' + str(count))

                print('Keyword : ' + keyword['similar_keyword'] + '  -  ' + str(keyword['id']))


if __name__ == '__main__':
    search_web_page_texts()
