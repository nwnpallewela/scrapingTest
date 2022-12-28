import csv

key_phrases_map = {}
sdg_count = 0
key_phrases_map[sdg_count] = set()
with open('files/key_phrases.csv', mode='r') as key_phrases_csv_file:
    csv_reader = csv.DictReader(key_phrases_csv_file)
    for row in csv_reader:
        if str(row['value']) == '-':
            sdg_count = sdg_count + 1
            key_phrases_map[sdg_count] = set()
            continue
        key_phrases_map[sdg_count].add(str(row['value']).lower())


def init_similar_key_phrases_file():
    with open('files/similar_keyphrases.csv', mode='w') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword_id', 'similar_keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writeheader()


def write_similar_key_phrases(similar_kw_id_l, keyword_index_l, similar_keyword_l):
    with open('files/similar_keyphrases.csv', mode='a') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword_id', 'similar_keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writerow({'keyword_id': keyword_index_l,
                                                   'similar_keyword': similar_keyword_l,
                                                   'id': similar_kw_id_l})


def init_key_phrases_file():
    with open('files/keyphrases.csv', mode='w') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writeheader()


def write_key_phrases(keyword_index_l, keyword_l):
    with open('files/keyphrases.csv', mode='a') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['id', 'keyword']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writerow({'keyword': keyword_l,
                                                   'id': keyword_index_l})


def init_topics_key_phrases_file():
    with open('files/topics_keyphrases.csv', mode='w') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['topic_id', 'keyword_id']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writeheader()


def write_topics_key_phrases(topic_id, keyword_index_l):
    with open('files/topics_keyphrases.csv', mode='a') as similar_keywords_csv_file_l:
        similar_keywords_fieldnames = ['topic_id', 'keyword_id']
        similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                          fieldnames=similar_keywords_fieldnames)
        similar_keywords_csv_file_writer.writerow({'topic_id': topic_id,
                                                   'keyword_id': keyword_index_l})


if __name__ == '__main__':
    init_topics_key_phrases_file()
    init_similar_key_phrases_file()
    init_key_phrases_file()
    phrase_id = 0
    phrases_map = {}
    for topic in key_phrases_map.keys():
        for phrase in key_phrases_map.get(topic):
            if phrases_map.get(phrase) is None:
                phrases_map[phrase] = phrase_id
                write_key_phrases(phrase_id, phrase)
                write_topics_key_phrases(topic, phrase_id)
                write_similar_key_phrases(phrase_id, phrase_id, phrase)
                phrase_id = phrase_id + 1
            else:
                id_p = phrases_map.get(phrase)
                write_topics_key_phrases(topic, id_p)
                write_similar_key_phrases(id_p, id_p, phrase)

    print()
