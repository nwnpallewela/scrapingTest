import csv

council_map = {}
with open('../crawler/files/council_map.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        council_map[row['id']] = row['council']

key_words_map = {}
with open('../keyword-matching/keywords.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        key_words_map[row['id']] = row['keyword']

topic_key_words_map = {}
with open('../keyword-matching/topic_key_words.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        topic_key_words_map[row['keyword_id']] = row['topic_id']

topic_page_map = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {},
                  '10': {}, '11': {}, '12': {}, '13': {}, '14': {}, '15': {}, '16': {}}
if __name__ == '__main__':
    # with open("../keyword-matching/files/matching_phrases.csv") as matching_phrases:
    with open("../keyword-matching/files/matching_key_words.csv") as matching_phrases:
        matching_phrases_reader = csv.DictReader(matching_phrases)
        for row in matching_phrases_reader:
            topic = topic_key_words_map.get(row['keyword_id'])
            page = row['page_id']
            site = row['site_id']
            if topic_page_map.get(str(topic)) is not None:
                if topic_page_map.get(str(topic)).get(page) is not None:
                    obj = topic_page_map.get(str(topic)).get(page)
                    obj['count'] = obj['count'] + 1
                else:
                    topic_page_map[str(topic)][page] = {'site_id': site, 'page_id': page, 'count': 1}
    for topic_pages in topic_page_map:
        with open("files/" + topic_pages + '.csv', mode='w') as topic_pages_file:
            topic_pages_file_writer = csv.DictWriter(topic_pages_file, fieldnames=['site_id', 'page_id', 'count'])
            topic_pages_file_writer.writeheader()
            for page in topic_page_map[topic_pages]:
                topic_pages_file_writer.writerow(topic_page_map[topic_pages][page])
    print('Done')


