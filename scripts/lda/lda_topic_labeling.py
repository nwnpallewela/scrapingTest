import gensim
import spacy
import xlrd
from gensim import corpora
from gensim.models import LdaModel
from gensim.test.utils import datapath
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords

stop_words = stopwords.words('english')

TEXTS_TOPICS_PRE_PROCESSED_XLSX = "../text-extractor/files/topicPagesExtractedTexts.xls"


def sent_to_words(sentences_l):
    for sentence in sentences_l:
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)  # deacc=True removes punctuations


def remove_stopwords(texts_l):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts_l]


def make_bigrams(texts_l):
    return [bigram_mod[doc] for doc in texts_l]


def lemmatization(texts_l, nlp_l, allowed_postags=['NOUN', 'ADJ']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts_l:
        doc = nlp_l(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


if __name__ == '__main__':
    nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
    for s in nlp.vocab.vectors:
        _ = nlp.vocab[s]
    wb_topics = xlrd.open_workbook('%s' % TEXTS_TOPICS_PRE_PROCESSED_XLSX)
    sheet_tp = wb_topics.sheet_by_index(0)
    sentences_tp = []
    topics_array = []
    for count in range(0, 55):
        sentences_tp.append(sheet_tp.cell_value(count, 4))
        topics_array.append(int(sheet_tp.cell_value(count, 3)))

    data_words = list(sent_to_words(sentences_tp))

    # Remove Stop Words
    data_words_nostops = remove_stopwords(data_words)
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    data_words_bigrams = make_bigrams(data_words_nostops)
    data_lemmatized = lemmatization(data_words_bigrams, nlp, allowed_postags=['NOUN', 'ADJ'])
    # Create Dictionary
    id2word = corpora.Dictionary(data_lemmatized)
    # Create Corpus
    texts = data_lemmatized
    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]
    count = 0
    topic_id = 0
    for topic_id in range(0, 17):
        if topic_id != 9:
            # print("model" + str(topic_id) + ".csv")
            temp_file = datapath("model" + str(topic_id) + ".csv")
            lda_model = LdaModel.load(temp_file)
            for count in range(0, 55):
                if topics_array[count] == topic_id:
                    vector = lda_model[corpus[count]]
                    best_topic_vec = vector[0][0]
                    for val in vector[0]:
                        if best_topic_vec[1] < val[1]:
                            best_topic_vec = val
                    best_topic = lda_model.show_topic(best_topic_vec[0])
                    print(str(topic_id) + " - " + str(best_topic[0]))
