import csv
import os
import re
import numpy as np
import pandas as pd
from pprint import pprint
import pyLDAvis.gensim_models
import xlrd
from gensim.models import LdaModel
from gensim.test.utils import datapath

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess

import spacy

# Plotting tools
import pyLDAvis
import gensim  # don't skip this
import matplotlib.pyplot as plt

# NLTK Stop words
from nltk.corpus import stopwords

TEXTS_TOPICS_PRE_PROCESSED_XLSX = "../text-extractor/files/topicPagesExtractedTexts.xls"

stop_words = stopwords.words('english')
page_lda_topics_file_fieldnames = ['site_id', 'page_id', 'topic', 'lda_topic']


def init_page_lda_topics():
    with open('lda_files/page_lda_topics.csv', mode='w') as page_lda_topics_file:
        page_lda_topics_file_writer_l = csv.DictWriter(page_lda_topics_file,
                                                       fieldnames=page_lda_topics_file_fieldnames)
        page_lda_topics_file_writer_l.writeheader()


def write_page_lda_topics(site_id, page_id, topic, lda_topic):
    with open('lda_files/page_lda_topics.csv', mode='a') as page_lda_topics_file:
        page_lda_topics_file_writer_l = csv.DictWriter(page_lda_topics_file,
                                                       fieldnames=page_lda_topics_file_fieldnames)
        page_lda_topics_file_writer_l.writerow({'site_id': site_id,
                                                'page_id': page_id,
                                                'topic': topic,
                                                'lda_topic': lda_topic})


sent_map = {}
page_text_map = {}
with open('../pre-processing/files/web_pages_text_sent_token.csv', mode='r') as sent_csv_file:
    csv_reader = csv.DictReader(sent_csv_file)
    for row in csv_reader:
        sent_map[row['sent']] = row['text']
        if page_text_map.get(row['page']) is None:
            page_text_map[row['page']] = row['text']
        else:
            page_text_map[row['page']] = str(page_text_map.get(row['page'])) + row['text']


def sent_to_words(sentences_l):
    for sentence in sentences_l:
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)  # deacc=True removes punctuations


def remove_stopwords(texts_l):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts_l]


def make_bigrams(texts_l):
    return [bigram_mod[doc] for doc in texts_l]


def make_trigrams(texts_l):
    return [trigram_mod[bigram_mod[doc]] for doc in texts_l]


def lemmatization(texts_l, nlp_l, allowed_postags=['NOUN', 'ADJ']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts_l:
        doc = nlp_l(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


if __name__ == '__main__':
    init_page_lda_topics()
    nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
    for s in nlp.vocab.vectors:
        _ = nlp.vocab[s]
    files = os.listdir('files')
    files = ['0.csv', '1.csv', '2.csv', '3.csv', '4.csv', '5.csv', '6.csv', '7.csv', '8.csv', '10.csv', '11.csv',
             '12.csv',
             '13.csv', '14.csv', '15.csv', '16.csv']
    wb_topics = xlrd.open_workbook('%s' % TEXTS_TOPICS_PRE_PROCESSED_XLSX)
    sheet_tp = wb_topics.sheet_by_index(0)
    sentences_tp = []
    topics_array = []
    for count in range(0, 55):
        sentences_tp.append(sheet_tp.cell_value(count, 4))
        topics_array.append(int(sheet_tp.cell_value(count, 3)))

    for file in files:
        print(file)
        sentences = []
        pages = []
        count = 0
        with open("files/" + str(file)) as topic_0:
            topic_0_reader = csv.DictReader(topic_0)
            for row in topic_0_reader:
                sentences.append(page_text_map[row['page_id']])
                pages.append(row['page_id'])
                count = count + 1

        for sen in sentences_tp:
            sentences.append(sen)
        data_words = list(sent_to_words(sentences))

        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        # Remove Stop Words
        data_words_nostops = remove_stopwords(data_words)
        # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
        # python3 -m spacy download en
        # nlp = spacy.load('en', disable=['parser', 'ner'])
        # Form Bigrams
        data_words_bigrams = make_bigrams(data_words_nostops)
        data_lemmatized = lemmatization(data_words_bigrams, nlp, allowed_postags=['NOUN', 'ADJ'])

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)

        # Create Corpus
        texts = data_lemmatized

        # Term Document Frequency
        corpus = [id2word.doc2bow(text) for text in texts]

        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=20,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)
        temp_file = datapath("model" + file)
        lda_model.save(temp_file)
        lda_model = LdaModel.load(temp_file)
        # pprint(lda_model.print_topics())
        doc_lda = lda_model[corpus]
        # print('completed_building_LDA_model')

        # print('preparing vis...')
        # pyLDAvis.enable_notebook()
        # p = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
        # pyLDAvis.save_html(p, 'diagrams/' + file + '.html')
        for i in range(0, count):
            unseen_doc = corpus[i]
            vector = lda_model[unseen_doc]
            best_topic_vec = vector[0][0]
            for val in vector[0]:
                if best_topic_vec[1] < val[1]:
                    best_topic_vec = val
            best_topic = lda_model.show_topic(best_topic_vec[0])
            page_val = pages[i]
            site_val = str(page_val).split('_')[0]
            # print(str(pages[i]) + " - " + str(best_topic_vec[0]))
            write_page_lda_topics(site_val, page_val, file.replace('.csv', ''), best_topic_vec[0])
            # for word in best_topic:
            #     print("")
            # lda_topics_csv_file_writer.writerow(
            #    {'page_id': i, 'value': word[1], 'topic_kw': common_dictionary[int(word[0])]})
        for i in range(count + 1, count + len(sentences_tp)):
            if int(topics_array[i - count - 1]) == int(file.replace('.csv', '')):
                vector = lda_model[corpus[i]]
                best_topic_vec = vector[0][0]
                for val in vector[0]:
                    if best_topic_vec[1] < val[1]:
                        best_topic_vec = val
                best_topic = lda_model.show_topic(best_topic_vec[0])
                print(str(topics_array[i - count - 1]) + " - " + str(best_topic_vec[0]))
