import csv

import spacy
import xlrd
import xlwt
from spacy.matcher.phrasematcher import PhraseMatcher

from utils import get_spacy_document

matching_phrases_fieldnames = ['site_id', 'page_id', 'sent_id', 'keyword_id', 'similar_kw_id', 'phrases_count']
matching_kw_fieldnames = ['site_id', 'page_id', 'sent_id', 'keyword_id', 'similar_kw_id', 'page_keyword']
TEXTS_PRE_PROCESSED = '../pre-processing/files/web_pages_text_sent_token-bk.csv'
TEXTS_TOKENIZED_KEY_WORDS = '../keyword-extraction/files/yake_key_words_sent_tokenize.csv'
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
    with open('files/matching_tokenized_phrases.csv', mode='w') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writeheader()


def init_matching_keywords():
    with open('files/matching_tokenized_key_words.csv', mode='w') as matching_kw_csv_file_l:
        matching_kw_csv_file_writer_l = csv.DictWriter(matching_kw_csv_file_l,
                                                       fieldnames=matching_kw_fieldnames)
        matching_kw_csv_file_writer_l.writeheader()


def write_matching_phrases(site_id, page_id, sent_id_l, keyword_index_l, similar_kw_id_l, phrases_count):
    with open('files/matching_tokenized_phrases.csv', mode='a') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=matching_phrases_fieldnames)
        matching_phrases_csv_file_writer_l.writerow({'site_id': site_id,
                                                     'page_id': page_id,
                                                     'sent_id': sent_id_l,
                                                     'keyword_id': keyword_index_l,
                                                     'similar_kw_id': similar_kw_id_l,
                                                     'phrases_count': phrases_count})


def write_matching_keywords(site_id, page_id, sent_id_l, keyword_index_l, similar_kw_id_l, page_keyword):
    with open('files/matching_tokenized_key_words.csv', mode='a') as matching_kw_csv_file_l:
        matching_kw_csv_file_writer_l = csv.DictWriter(matching_kw_csv_file_l,
                                                       fieldnames=matching_kw_fieldnames)
        matching_kw_csv_file_writer_l.writerow({'site_id': site_id,
                                                'page_id': page_id,
                                                'sent_id': sent_id_l,
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

    # nlp.add_pipe('setCustomBoundaries', before='parser')
    with open(TEXTS_PRE_PROCESSED, mode='r') as pre_processed_text:
        pre_processed_text_reader = csv.DictReader(pre_processed_text)
        for pre_processed_text_line in pre_processed_text_reader:
            for keyword in similar_keywords_list:
                spacy_obj = get_spacy_document(str(pre_processed_text_line['text']), nlp)
                matching_phrases = search_for_keyword(keyword['similar_keyword'], spacy_obj, nlp)
                # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                if len(matching_phrases) > 0:
                    write_matching_phrases(pre_processed_text_line['site'], pre_processed_text_line['page'],
                                           pre_processed_text_line['sent'],
                                           keyword['keyword_id'], keyword['id'], len(matching_phrases))
            print('Site / Page : ' + str(pre_processed_text_line['site']) + " / "
                  + str(pre_processed_text_line['page']))


def search_web_page_keywords():
    print("Searching Web page Keywords")
    init_matching_keywords()
    with open(TEXTS_TOKENIZED_KEY_WORDS, mode='r') as keywords_csv:
        keywords_csv_reader = csv.DictReader(keywords_csv)
        for pre_processed_text_line in keywords_csv_reader:
            for keyword in similar_keywords_list:
                # spacy_obj = get_spacy_document(str(pre_processed_text_line['KeyWord']), nlp)
                # matching_phrases = search_for_keyword(keyword['similar_keyword'], spacy_obj, nlp)
                # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                # if len(matching_phrases) > 0:
                if str(pre_processed_text_line['KeyWord']).__contains__(keyword['similar_keyword']):
                    write_matching_keywords(pre_processed_text_line['Site'], pre_processed_text_line['Page']
                                            , pre_processed_text_line['Sent'], keyword['keyword_id'], keyword['id'],
                                            str(pre_processed_text_line['KeyWord']))
                # print('Page / Site : ' + pre_processed_text_line['Page'] + ' - ' + keyword['keyword_id'])
            print('Site /  Page: ' + pre_processed_text_line['Site'] + ' - ' + str(pre_processed_text_line['Page']))


if __name__ == '__main__':
    search_web_page_texts()
    search_web_page_keywords()
