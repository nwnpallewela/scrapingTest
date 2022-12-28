# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import os
import urllib

from scripts.lda.lda_models import simplify, preprocess, viz_model, test_eta, create_eta

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import json
import xlsxwriter
from boilerpy3 import extractors
import lxml
from gensim.models import LdaModel
from lxml.html.clean import Cleaner
import xlrd
import xlwt
from nltk.corpus import stopwords
from spacy.matcher.phrasematcher import PhraseMatcher

import yake
import spacy
from scipy import spatial
import enchant
from gensim.test.utils import common_texts, datapath
from gensim.corpora.dictionary import Dictionary
from gensim.parsing.preprocessing import remove_stopwords, strip_punctuation, preprocess_string, strip_short, stem_text

import warnings

warnings.filterwarnings(action='ignore', category=UserWarning)
import gensim
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt

# matplotlib inline
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

WEB_PAGE_TEXTS_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/webPageTexts.xls'

TEXTS_PRE_PROCESSED_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/webPageTextsPreProcessed.xls'

TEXTS_KEY_VALUES_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/webPageTextsKeyValues.xls'
TEXTS_YAKE_KEY_VALUES_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/webPageTextsYakeKeyValues.xlsx'

TOPICS_KEY_WORDS_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/TopicsKeyWords.xlsx'
MATCHING_PHRASES_XLSX = '/Users/nuwan/PycharmProjects/scrapingTest/MatchingPhrases.xlsx'

PAGE_COUNT = 1229
SITE_COUNT = 1

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

dictionary = enchant.Dict('en_US')

key_words_topic_map = {}
with open('topic_key_words.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_topic_map[row['keyword_id']] = row['topic_id']

key_words_map = {}
with open('keywords.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_map[row['id']] = row['keyword']


def setCustomBoundaries(doc):
    # traversing through tokens in document object
    for token in doc[:-1]:
        if token.text == ';':
            doc[token.i + 1].is_sent_start = True
        if token.text == ".":
            doc[token.i + 1].is_sent_start = False
    return doc


def search_for_keyword(keyword, doc_obj, nlp_o):
    phrase_matcher = PhraseMatcher(nlp_o.vocab)
    phrase_list = [nlp_o(keyword)]
    phrase_matcher.add("Text Extractor", None, *phrase_list)

    matched_items = phrase_matcher(doc_obj)

    matched_text = []
    for match_id, start, end in matched_items:
        text = nlp_o.vocab.strings[match_id]
        span = doc_obj[start: end]
        matched_text.append(span.sent.text)

    return matched_text


def get_similar_words(keyword, nlp_o):
    similarity_list = []

    keyword_vector = get_spacy_document(keyword, nlp_o).vector

    for tokens in nlp_o.vocab:
        if tokens.has_vector:
            if tokens.is_lower:
                if tokens.is_alpha:
                    similarity_list.append((tokens, cosine_similarity(keyword_vector, tokens.vector)))

    similarity_list = sorted(similarity_list, key=lambda item: -item[1])
    similarity_list = similarity_list[:30]

    top_similar_words = [item[0].text for item in similarity_list]

    top_similar_words = top_similar_words[:3]
    top_similar_words.append(keyword)

    for token in nlp_o(keyword):
        top_similar_words.insert(0, token.lemma_)

    for words in top_similar_words:
        if words.endswith("s"):
            top_similar_words.append(words[0:len(words) - 1])

    top_similar_words = list(set(top_similar_words))

    # top_similar_words = [words for words in top_similar_words if enchant_dict.check(words) == True]
    top_similar_words = [words for words in top_similar_words if dictionary.check(words)]

    return ", ".join(top_similar_words)


def get_spacy_document(text, nlp_o):
    main_doc = nlp_o(text)  # create spacy document object
    return main_doc


# method to find cosine similarity
def cosine_similarity(vector_1, vector_2):
    # return cosine distance
    return 1 - spatial.distance.cosine(vector_1, vector_2)


def condense_newline(text):
    return '\n'.join([p for p in re.split('\n|\r', text) if len(p) > 0])


def parse_html(html_path):
    # Text extraction with boilerpy3
    html_extractor = extractors.ArticleExtractor()
    return condense_newline(html_extractor.get_content_from_file(html_path))


def html_to_text(folder):
    parsed_texts = []
    file_paths = os.listdir(folder)

    for filepath in file_paths:
        filepath_full = os.path.join(folder, filepath)
        if filepath_full.endswith(".html"):
            try:
                parsed_texts.append(parse_html(filepath_full))
            except:
                print("An error occurred parsing html from boilerpy3")
    return parsed_texts


def html_file_to_text(file):
    parsed_texts = []
    try:
        parsed_texts = [parse_html(file)]
    except:
        print("An error occurred parsing html from boilerpy3 " + file)
    parsed_text = ""
    for p in parsed_texts:
        parsed_text += p
    return parsed_text


def save_file_html(folder, name, data):
    if not os.path.exists(folder):
        os.makedirs(folder)
    out_file_name = folder + "/" + name
    out_file = open(out_file_name, "w")
    out_file.write(str(data))
    out_file.close()


def clean_html_text(file_name_c):
    try:
        cleaned_text = str(lxml.html.tostring(cleaner.clean_html(lxml.html.parse(file_name_c))))
    except:
        print("Error while cleaning data")
    return cleaned_text


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def gensim_preprocess(text):
    # clean text based on given filters
    custom_filters = [lambda x: x.lower(),
                      remove_stopwords,
                      strip_punctuation]
    text = preprocess_string(text, custom_filters)

    return text


if __name__ == '__main__':
    # scraped_dir = '/Users/nuwan/Documents/scrapeData'
    # parsed_texts = html_to_text(scraped_dir)
    #
    # Data Extraction
    print_progress_bar(0, 2, prefix='Filter Web Pages    :', suffix='Complete', length=50)
    f = open('configs.json')
    config = json.load(f)
    if config.get('enableDataExtraction'):
        workbook = xlsxwriter.Workbook('webPageTexts.xls')
        with open('web_page_list.csv', mode='w') as web_pages:
            doc_field_names = ['site_id', 'page_id', 'page_url']
            web_pages_writer = csv.DictWriter(web_pages, fieldnames=doc_field_names)
            web_pages_writer.writeheader()
            site_count = 0
            for i in config['sites']:
                worksheet = workbook.add_worksheet(i['name'])
                content = set([])
                print(i['name'])
                url = i['url']
                content.add(url)
                urls = [url]
                count = 0
                while len(content) > 0 and len(content) > count and count < (PAGE_COUNT + 1):
                    print(url)
                    url = urls[count]
                    try:
                        if url[0:6] == 'https:' and str(url).startswith(i['base']):
                            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                            page = urlopen(req)
                        else:
                            req = Request(i.get('base') + url, headers={'User-Agent': 'Mozilla/5.0'})
                            page = urlopen(req)
                    except:
                        print("An error occurred.")
                        count = count + 1
                        continue
                    soup = BeautifulSoup(page, 'html.parser')
                    save_file_html("/Users/nuwan/PycharmProjects/scrapingTest/files/" + i['name'], str(count) + ".html",
                                   soup)
                    worksheet.write("A" + str(count), count)
                    worksheet.write("B" + str(count), url)
                    file_name = "/Users/nuwan/PycharmProjects/scrapingTest/files/" + i['name'] + "/" + str(
                        count) + ".html"
                    worksheet.write("C" + str(count), html_file_to_text(file_name))
                    worksheet.write("D" + str(count), clean_html_text(file_name))
                    web_pages_writer.writerow({'site_id': site_count, 'page_id': count, 'page_url': url})
                    for tags in i['linkTags']:
                        if tags.get('class') is not None:
                            regex = re.compile(tags['class'])
                            content_lis = soup.find_all(tags['tag'], attrs={'class': regex})
                        else:
                            content_lis = soup.find_all(tags['tag'])
                        for li in content_lis:
                            link = li.get(tags['urlProperty'])
                            if link is not None and not content.__contains__(
                                    link) and link != "#" and " " not in link and (
                                    str(link).startswith("http") or str(link).startswith("/")):
                                content.add(link)
                                urls.append(link)

                    count = count + 1
                    print(count)
                site_count = site_count + 1
            print('More pages to check ' + str(len(content)))
            workbook.close()

    # Data pre processing
    if config.get('enablePreProcessing'):
        wb = xlrd.open_workbook('%s' % WEB_PAGE_TEXTS_XLSX)
        wb_w = xlwt.Workbook()
        stop = stopwords.words('english')
        for j in range(0, SITE_COUNT):
            sheet = wb.sheet_by_index(j)
            sheet_w = wb_w.add_sheet(sheet.name)
            for i in range(0, PAGE_COUNT):
                try:
                    val = str(sheet.cell_value(i, 2)).lower().replace('[^/w/s]', '')
                    val = ' '.join(x for x in val.split() if x not in stop)
                    sheet_w.write(i, 0, val)
                except:
                    print("Error extracting text")
                # sheet_w.write(i, 1, str(sheet.cell_value(i, 3)).lower().replace('[^/w/s]', ''))
            wb_w.save(TEXTS_PRE_PROCESSED_XLSX)
    print_progress_bar(1, 2, prefix='Filter Web Pages    :', suffix='Complete', length=50)

    if config.get('enableYake'):
        kw_extractor = yake.KeywordExtractor()
        wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
        wb_w_y = xlwt.Workbook()
        with open('yake_key_words.csv', mode='w') as stock_prices:
            fieldnames = ['Page', 'KeyWord', 'Value']
            key_words_writer = csv.DictWriter(stock_prices, fieldnames=fieldnames)
            key_words_writer.writeheader()
            print_progress_bar(0, PAGE_COUNT, prefix='YAKE Keyword Extract:', suffix='Complete', length=50)
            for j in range(0, SITE_COUNT):
                sheet = wb.sheet_by_index(j)
                sheet_w = wb_w_y.add_sheet(sheet.name)
                count = 1
                row = 1
                sheet_w.write(0, 0, 'Page')
                sheet_w.write(0, 1, 'KeyWord')
                sheet_w.write(0, 2, 'Value')
                for i in range(0, PAGE_COUNT):
                    keywords = kw_extractor.extract_keywords(str(sheet.cell_value(i, 0)))

                    for word in keywords:
                        sheet_w.write(row, 0, count)
                        sheet_w.write(row, 1, word[0])
                        sheet_w.write(row, 2, word[1])
                        key_words_writer.writerow({'Page': count, 'KeyWord': word[0], 'Value': word[1]})
                        row = row + 1
                    count = count + 1
                    print_progress_bar(i + 1, PAGE_COUNT, prefix='YAKE Keyword Extract:', suffix='Complete', length=50)
                    # sheet_w.write(i, 1, str(sheet.cell_value(i, 3)).lower().replace('[^/w/s]', ''))
        wb_w_y.save('%s' % TEXTS_YAKE_KEY_VALUES_XLSX)

    if config.get('enableTopicsExtractionYake'):
        kw_extractor = yake.KeywordExtractor()
        topics_dir = '/Users/nuwan/PycharmProjects/scrapingTest/topics'
        file_paths = os.listdir(topics_dir)
        wb_w = xlwt.Workbook()

        for filepath in file_paths:
            if not str(filepath).startswith('.'):
                filepath_full = os.path.join(topics_dir, filepath)
                pages = os.listdir(filepath_full)
                worksheet = wb_w.add_sheet(filepath)
                count = 0
                for page in pages:
                    page_path_full = os.path.join(filepath_full, page)
                    txt = parse_html(page_path_full)
                    worksheet.write(1, count, 'word')
                    worksheet.write(1, count + 1, 'value')
                    try:
                        key_words = kw_extractor.extract_keywords(txt)
                        col = 2
                        for word in key_words:
                            worksheet.write(col, count, word[0])
                            worksheet.write(col, count + 1, word[1])
                            col = col + 1
                    except:
                        print("Error extracting keywords")
                    count = count + 2
        wb_w.save('%s' % TOPICS_KEY_WORDS_XLSX)
    print_progress_bar(2, 2, prefix='Filter Web Pages    :', suffix='Complete', length=50)

    if config.get('enableSpacy'):
        keywords_list = []
        processed_keywords_set = set()
        with open('keywords.csv', mode='r') as keywords_csv_file:
            csv_reader = csv.DictReader(keywords_csv_file)
            for row in csv_reader:
                keywords_list.append(row['id'])
        nlp = spacy.load('en_core_web_lg')
        for s in nlp.vocab.vectors:
            _ = nlp.vocab[s]
        # nlp.add_pipe('setCustomBoundaries', before='parser')
        wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
        with open('similar_keywords.csv', mode='w') as similar_keywords_csv_file:
            with open('matching_phrases.csv', mode='w') as matching_phrases_csv_file:
                similar_keywords_fieldnames = ['id', 'keyword_id', 'similar_keyword']
                matching_phrases_fieldnames = ['site_id', 'page_id', 'keyword_id', 'similar_kw_id', 'phrases_count']
                similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file,
                                                                  fieldnames=similar_keywords_fieldnames)
                matching_phrases_csv_file_writer = csv.DictWriter(matching_phrases_csv_file,
                                                                  fieldnames=matching_phrases_fieldnames)
                similar_keywords_csv_file_writer.writeheader()
                matching_phrases_csv_file_writer.writeheader()
                keyword_index = 0
                wb_w_y = xlwt.Workbook()
                sheet_w = wb_w_y.add_sheet("matching phrases")
                sheet_w.write(0, 1, 'site_id')
                sheet_w.write(0, 2, 'page_id')
                sheet_w.write(0, 3, 'key_word_id')
                sheet_w.write(0, 4, 'key_word')
                sheet_w.write(0, 5, 'similar_word')
                sheet_w.write(0, 6, 'phrase')
                sheet_w.write(0, 0, 'id')
                row_id = 1
                similar_kw_id = 0
                similar_keywords_map = {}
                for keyword_id in keywords_list:
                    keyword_i = key_words_map[keyword_id]
                    for j in range(0, SITE_COUNT):
                        sheet = wb.sheet_by_index(j)
                        similar_keywords = get_similar_words(keyword_i, nlp)
                        similar_keywords = similar_keywords + ',' + keyword_i
                        similar_keywords_array = []
                        topic_id = key_words_topic_map.get(keyword_id)
                        if topic_id in None:
                            topic_id = -1
                        if similar_keywords_map.__contains__(keyword_id):
                            similar_keywords_array = similar_keywords_map.get(topic_id)
                        else:
                            similar_keywords_map[topic_id] = similar_keywords_array
                        for similar_keyword in similar_keywords.split(','):
                            if not similar_keywords_array.__contains__(similar_keyword):
                                similar_keywords_csv_file_writer.writerow({'keyword_id': keyword_index,
                                                                           'similar_keyword': similar_keyword,
                                                                           'id': similar_kw_id})
                                similar_keywords_array.append(similar_keyword)
                                # similar_keyword_obj = get_spacy_document(similar_keyword, nlp)
                                # keyword_obj = get_spacy_document("sustainability", nlp)
                                # print(get_similar_words("safety", nlp))
                                for i in range(0, PAGE_COUNT):
                                    spacy_obj = get_spacy_document(str(sheet.cell_value(i, 0)), nlp)
                                    matching_phrases = search_for_keyword(similar_keyword, spacy_obj, nlp)
                                    # value = cosine_similarity(spacy_obj.vector, keyword_obj.vector)
                                    if len(matching_phrases) > 0:
                                        matching_phrases_csv_file_writer.writerow({'site_id': j,
                                                                                   'page_id': i,
                                                                                   'keyword_id': keyword_index,
                                                                                   'similar_kw_id': similar_kw_id,
                                                                                   'phrases_count': len(
                                                                                       matching_phrases)})
                                        for phrase in matching_phrases:
                                            sheet_w.write(row_id, 1, j)
                                            sheet_w.write(row_id, 2, i)
                                            sheet_w.write(row_id, 3, keyword_index)
                                            sheet_w.write(row_id, 4, keyword_i)
                                            sheet_w.write(row_id, 5, similar_keyword)
                                            sheet_w.write(row_id, 6, phrase)
                                            sheet_w.write(row_id, 0, row_id)
                                            row_id = row_id + 1
                                        # print(str(i) + ' : ' + str(len(matching_phrases)))
                                        # print(matching_phrases)
                                        # print('----------\n')
                                if i % 50 == 0:
                                    print('Page : ' + str(i))
                            similar_kw_id = similar_kw_id + 1
                    keyword_index = keyword_index + 1
                    print('Keyword : ' + keyword_i + '  -  ' + str(keyword_index))
                wb_w_y.save('%s' % MATCHING_PHRASES_XLSX)

    text_docs = []
    if config.get('enableLDA') | config.get('enableGuidedLDA'):
        wb = xlrd.open_workbook('%s' % TEXTS_PRE_PROCESSED_XLSX)
        for j in range(0, SITE_COUNT):
            sheet = wb.sheet_by_index(j)
            for i in range(0, PAGE_COUNT):
                pre_processed_text = gensim_preprocess(str(sheet.cell_value(i, 0)))
                text_docs.append(pre_processed_text)

    if config.get('enableLDA'):
        print("Running LDA")
        common_dictionary = Dictionary(text_docs)
        common_corpus = [common_dictionary.doc2bow(text) for text in text_docs]
        lda_m = LdaModel(common_corpus, num_topics=100)

        # temp_file = datapath("model")
        # lda.save(temp_file)
        # lda_m = LdaModel.load(temp_file)
        with open('lda_topics.csv', mode='w') as lda_topics_csv_file:
            field_names = ['page_id', 'topic_kw', 'value']
            lda_topics_csv_file_writer = csv.DictWriter(lda_topics_csv_file, fieldnames=field_names)
            lda_topics_csv_file_writer.writeheader()
            for i in range(0, PAGE_COUNT):
                unseen_doc = common_corpus[i]
                vector = lda_m[unseen_doc]
                best_topic_vec = vector[0]
                for val in vector:
                    if best_topic_vec[1] < val[1]:
                        best_topic_vec = val
                best_topic = lda_m.show_topic(best_topic_vec[0])
                for word in best_topic:
                    lda_topics_csv_file_writer.writerow(
                        {'page_id': i, 'value': word[1], 'topic_kw': common_dictionary[int(word[0])]})

    if config.get('enableGuidedLDA'):
        print('Guided LDA')
        txt = text_docs
        corp = [preprocess(line) for line in txt]
        dictionary = gensim.corpora.Dictionary(corp)
        # len(dictionary)
        bow = [dictionary.doc2bow(line) for line in corp]
        apriori_original = {
            'poor': 2, 'poverty': 2, 'homeless': 2,
            'hunger': 1, 'diet': 1, 'food': 1,
            'education': 0, 'school': 0, 'student': 0
        }
        eta = create_eta(apriori_original, dictionary, 30)
        test_eta(eta, dictionary, corp, txt, 30)
        # test_eta('auto', dictionary, corp, txt, ntopics=2)
