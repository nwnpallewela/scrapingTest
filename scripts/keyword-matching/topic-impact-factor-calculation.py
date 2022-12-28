import csv
import collections
import spacy
import xlrd
import xlwt
from spacy.matcher.phrasematcher import PhraseMatcher

from utils import get_spacy_document

council_map = {}
with open('../crawler/files/council_map.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        council_map[row['id']] = row['council']

keyphrase_topics_map = {}
with open('files/topics_keyphrases.csv', mode='r') as council_csv_file:
    csv_reader = csv.DictReader(council_csv_file)
    for row in csv_reader:
        if keyphrase_topics_map.get(row['keyword_id']) is None:
            keyphrase_topics_map[row['keyword_id']] = []
        keyphrase_topics_map[row['keyword_id']].append(row['topic_id'])

similar_keywords_list = []

with open('files/similar_keywords.csv', mode='r') as keywords_csv_file:
    csv_reader = csv.DictReader(keywords_csv_file)
    for row in csv_reader:
        similar_keywords_list.append(row)


def init_matching_phrases():
    with open('files/matching_phrases_with_impact.csv', mode='w') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=['site_id', 'topic_id', 'impact', 'page_id'])
        matching_phrases_csv_file_writer_l.writeheader()


def write_matching_phrases(site_id, topic_id, impact, page_id):
    with open('files/matching_phrases_with_impact.csv', mode='a') as matching_phrases_csv_file_l:
        matching_phrases_csv_file_writer_l = csv.DictWriter(matching_phrases_csv_file_l,
                                                            fieldnames=['site_id', 'topic_id', 'impact', 'page_id'])
        matching_phrases_csv_file_writer_l.writerow({'site_id': site_id,
                                                     'topic_id': topic_id,
                                                     'impact': impact,
                                                     'page_id': page_id})


if __name__ == '__main__':
    init_matching_phrases()
    impact_map = {}
    with open('files/matching_keyphrases.csv', mode='r') as matching_keyphrases_csv_file:
        csv_reader = csv.DictReader(matching_keyphrases_csv_file)
        for row in csv_reader:
            if impact_map.get(row['site_id']) is None:
                impact_map[row['site_id']] = {}

            site = impact_map[row['site_id']]
            topics = keyphrase_topics_map[row['keyword_id']]
            for topic in topics:
                if site.get(topic) is None:
                    site[topic] = {}
                topic_pages = site[topic]
                if topic_pages.get(row['page_id']) is None:
                    topic_pages[row['page_id']] = 1
                else:
                    topic_pages[row['page_id']] = topic_pages[row['page_id']] + 1
    restructured_map = {}
    for site in impact_map.keys():
        if restructured_map.get(site) is None:
            restructured_map[site] = {}
        for topic in impact_map[site].keys():
            if restructured_map.get(site).get(topic) is None:
                restructured_map[site][topic] = {}
            for page in impact_map[site][topic].keys():
                if restructured_map.get(site).get(topic).get(impact_map[site][topic][page]) is None:
                    restructured_map[site][topic][impact_map[site][topic][page]] = []
                restructured_map[site][topic][impact_map[site][topic][page]].append(page)
    for site in restructured_map.keys():
        for topic in restructured_map[site].keys():
            impact_values = restructured_map[site][topic].keys()
            od = collections.OrderedDict(sorted(restructured_map[site][topic].items(), reverse=True))
            for impact_factor in od.keys():
                for page in od[impact_factor]:
                    print(site + ',' + topic + ',' + str(impact_factor) + ',' + page)
                    write_matching_phrases(site, topic, impact_factor, page)
    print()
