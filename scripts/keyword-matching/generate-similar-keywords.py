import csv
import spacy
import xlrd
import xlwt
from scipy import spatial
import enchant

from utils import get_spacy_document
from utils import cosine_similarity


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

keywords_list = []
processed_keywords_set = set()


def init_similar_keywords_file():
    with open('files/similar_keywords.csv', mode='w') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword_id', 'similar_keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writeheader()


def write_similar_keyword(similar_kw_id_l, keyword_index_l, similar_keyword_l):
    with open('files/similar_keywords.csv', mode='a') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword_id', 'similar_keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writerow({'keyword_id': keyword_index_l,
                                                   'similar_keyword': similar_keyword_l,
                                                   'id': similar_kw_id_l})


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

    return ",".join(top_similar_words)


if __name__ == '__main__':
    # init_similar_keywords_file()
    with open('keywords.csv', mode='r') as keywords_csv_file:
        csv_reader = csv.DictReader(keywords_csv_file)
        for row in csv_reader:
            keywords_list.append(row['id'])
    nlp = spacy.load('en_core_web_lg')
    for s in nlp.vocab.vectors:
        _ = nlp.vocab[s]
    # nlp.add_pipe('setCustomBoundaries', before='parser')
    keyword_index = 175
    row_id = 1
    similar_kw_id = 175
    similar_keywords_map = {}
    for keyword_id in keywords_list:
        if int(keyword_id) > 57:
            keyword_i = key_words_map[keyword_id]
            similar_keywords = get_similar_words(keyword_i, nlp)
            similar_keywords = similar_keywords + ',' + keyword_i
            similar_keywords_array = []
            topic_id = key_words_topic_map.get(keyword_id)
            if topic_id is None:
                topic_id = -1
            if similar_keywords_map.__contains__(topic_id):
                similar_keywords_array = similar_keywords_map.get(topic_id)
            else:
                similar_keywords_map[topic_id] = similar_keywords_array
            for similar_keyword in similar_keywords.split(','):
                if not similar_keywords_array.__contains__(similar_keyword):
                    write_similar_keyword(similar_kw_id, keyword_id, similar_keyword)
                    similar_keywords_array.append(similar_keyword)
                    similar_kw_id = similar_kw_id + 1
            print('Keyword : ' + keyword_i + '  -  ' + str(keyword_i))
    print("Done!!")

