import csv

topic_lda_topics_map = {}
with open("lda_files/topic_lda_topics.csv") as topic_lda_topics:
    topic_lda_topics_reader = csv.DictReader(topic_lda_topics)
    for row in topic_lda_topics_reader:
        if topic_lda_topics_map.get(row['sgd_topic']) is not None:
            topic_lda_topics_map[row['sgd_topic']].append(row['lda_topic'])
        else:
            topic_lda_topics_map[row['sgd_topic']] = [row['lda_topic']]

page_lda_rows = []
with open("lda_files/page_lda_topics.csv") as page_lda_topics:
    page_lda_topics_reader = csv.DictReader(page_lda_topics)
    for row in page_lda_topics_reader:
        page_lda_rows.append(row)

if __name__ == '__main__':
    with open("lda_files/page_lda_topics_filtered.csv", mode='w') as page_lda_topics_filtered:
        csv_writer = csv.DictWriter(page_lda_topics_filtered, ['site_id', 'page_id', 'topic', 'lda_topic'])
        for row in page_lda_rows:
            if topic_lda_topics_map[row['topic']].__contains__(row['lda_topic']):
                csv_writer.writerow(row)
    print('Done')
