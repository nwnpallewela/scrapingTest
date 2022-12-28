import csv

import spacy
import xlrd
import xlwt
from spacy.matcher.phrasematcher import PhraseMatcher

from utils import get_spacy_document

matching_phrases_fieldnames = ['site_id', 'page_id', 'keyword_id', 'similar_kw_id', 'phrases_count']
matching_kw_fieldnames = ['site_id', 'page_id', 'keyword_id', 'similar_kw_id', 'page_keyword']
TEXTS_PRE_PROCESSED_XLSX = '../pre-processing/files/webPagesPreProcessedTexts.xls'
MATCHING_PHRASES_XLSX = 'files/matchingPhrases.xls'
SITE_COUNT = 2
PAGE_COUNT = 10000

council_map = {}
with open('../crawler/files/council_map.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        council_map[row['id']] = row['council']

key_words_map = {}
with open('keywords.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_map[row['id']] = row['keyword']

similar_keywords_list = []
nlp = spacy.load('en_core_web_lg')
for s in nlp.vocab.vectors:
    _ = nlp.vocab[s]

with open('files/similar_keywords.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        similar_keywords_list.append(row)


def init_matching_phrases():
    with open('files/matching_phrases.csv', mode='w') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writeheader()


def init_matching_keywords():
    with open('files/matching_key_words.csv', mode='w') as matching_kw_csv_file_l:
        matching_kw_csv_file_writer_l = csv.DictWriter(matching_kw_csv_file_l,
                                                       fieldnames=matching_kw_fieldnames)
        matching_kw_csv_file_writer_l.writeheader()


def write_matching_phrases(site_id, page_id, keyword_index_l, similar_kw_id_l, phrases_count):
    with open('files/matching_phrases.csv', mode='a') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writerow({'site_id': site_id,
                                                     'page_id': page_id,
                                                     'keyword_id': keyword_index_l,
                                                     'similar_kw_id': similar_kw_id_l,
                                                     'phrases_count': phrases_count})


def write_matching_keywords(site_id, page_id, keyword_index_l, similar_kw_id_l, page_keyword):
    with open('files/matching_key_words.csv', mode='a') as matching_kw_csv_file_l:
        matching_kw_csv_file_writer_l = csv.DictWriter(matching_kw_csv_file_l,
                                                       fieldnames=matching_kw_fieldnames)
        matching_kw_csv_file_writer_l.writerow({'site_id': site_id,
                                                'page_id': page_id,
                                                'keyword_id': keyword_index_l,
                                                'similar_kw_id': similar_kw_id_l,
                                                'page_keyword': page_keyword})


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
    init_matching_phrases()
    wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
    wb_w_y = xlwt.Workbook()
    # nlp.add_pipe('setCustomBoundaries', before='parser')
    for j in range(0, SITE_COUNT):
        sheet = wb.sheet_by_index(j)
        sheet_w = wb_w_y.add_sheet(council_map[str(j)])
        sheet_w.write(0, 1, 'site_id')
        sheet_w.write(0, 2, 'page_id')
        sheet_w.write(0, 3, 'key_word_id')
        sheet_w.write(0, 4, 'key_word')
        sheet_w.write(0, 5, 'similar_word')
        sheet_w.write(0, 6, 'phrase')
        sheet_w.write(0, 0, 'id')
        row_id = 1
        for keyword in similar_keywords_list:
            for i in range(0, PAGE_COUNT):
                spacy_obj = get_spacy_document(str(sheet.cell_value(i, 0)), nlp)
                matching_phrases = search_for_keyword(keyword['similar_keyword'], spacy_obj, nlp)
                # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                if len(matching_phrases) > 0:
                    write_matching_phrases(j, i, keyword['keyword_id'], keyword['id'], len(matching_phrases))
                    for phrase in matching_phrases:
                        sheet_w.write(row_id, 1, j)
                        sheet_w.write(row_id, 2, i)
                        sheet_w.write(row_id, 3, keyword['keyword_id'])
                        sheet_w.write(row_id, 4, key_words_map[keyword['keyword_id']])
                        sheet_w.write(row_id, 5, keyword['similar_keyword'])
                        sheet_w.write(row_id, 6, phrase)
                        sheet_w.write(row_id, 0, row_id)
                        row_id = row_id + 1

                print('Page : ' + str(i))
            print('Keyword : ' + keyword['similar_keyword'] + '  -  ' + str(keyword['id']))
    wb_w_y.save('%s' % MATCHING_PHRASES_XLSX)


def search_web_page_keywords():
    print("Searching Web page Keywords")
    init_matching_keywords()
    wb_w_y = xlwt.Workbook()
    sheet_w = wb_w_y.add_sheet("matching_keywords")
    for j in range(0, SITE_COUNT):
        sheet_w = wb_w_y.add_sheet(council_map[str(j)])
        sheet_w.write(0, 1, 'site_id')
        sheet_w.write(0, 2, 'page_id')
        sheet_w.write(0, 3, 'key_word_id')
        sheet_w.write(0, 4, 'key_word')
        sheet_w.write(0, 5, 'similar_word')
        sheet_w.write(0, 6, 'page_keyword')
        sheet_w.write(0, 0, 'id')
    with open('../keyword-extraction/files/yake_key_words.csv', mode='r') as keywords_csv:
        keywords_csv_reader = csv.DictReader(keywords_csv)
        row_id = 1
        for row_value in keywords_csv_reader:
            for keyword in similar_keywords_list:
                spacy_obj = get_spacy_document(str(row_value['KeyWord']), nlp)
                matching_phrases = search_for_keyword(keyword['similar_keyword'], spacy_obj, nlp)
                # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                if len(matching_phrases) > 0:
                    write_matching_keywords(row_value['Site'], row_value['Page'], keyword['keyword_id'], keyword['id'],
                                            matching_phrases[0])
                    # sheet_w.write(row_id, 1, row_value['Site'])
                    # sheet_w.write(row_id, 2, row_value['Page'])
                    # sheet_w.write(row_id, 3, keyword['keyword_id'])
                    # sheet_w.write(row_id, 4, key_words_map[keyword['keyword_id']])
                    # sheet_w.write(row_id, 5, keyword['similar_keyword'])
                    # sheet_w.write(row_id, 6, matching_phrases[0])
                    # sheet_w.write(row_id, 0, row_id)
                    row_id = row_id + 1
            print('Page : ' + row_value['Page'] + ' - ' + str(keyword['id']))
    wb_w_y.save('%s' % MATCHING_PHRASES_XLSX)


if __name__ == '__main__':
    search_web_page_texts()
    # search_web_page_keywords()
