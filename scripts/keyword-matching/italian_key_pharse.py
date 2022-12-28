import csv

if __name__ == '__main__':
    if False:
        with open('italian/indexed_italian_keyphrases.csv', mode='w') as similar_keywords_csv_file_l:
            similar_keywords_fieldnames = ['id', 'keyword_id']
            similar_keywords_csv_file_writer = csv.DictWriter(similar_keywords_csv_file_l,
                                                              fieldnames=similar_keywords_fieldnames)
            similar_keywords_csv_file_writer.writeheader()
            with open('italian/italian_keyphrases.csv', mode='r') as keywords_csv_file:
                csv_reader = csv.DictReader(keywords_csv_file)
                index = 0
                for row in csv_reader:
                    array = str(row['keyword'])
                    string = array.strip().lstrip().lower()
                    similar_keywords_csv_file_writer.writerow({'keyword_id': string,
                                                               'id': index})
                    index = index + 1
                    print(string)
    old_key_phrases = []
    english_key_phrases = []
    if True:
        with open('files/keyphrases.csv', mode='r') as similar_keywords_csv_file_l:
            similar_keywords_fieldnames = ['id', 'keyword']
            similar_keywords_csv_file_writer = csv.DictReader(similar_keywords_csv_file_l)
            for row in similar_keywords_csv_file_writer:
                old_key_phrases.append(row['keyword'])
        with open('italian/english_translate.csv', mode='r') as similar_keywords_csv_file_l:
            similar_keywords_csv_file_writer = csv.DictReader(similar_keywords_csv_file_l)
            for row in similar_keywords_csv_file_writer:
                english_key_phrases.append(row['keyword'])
        i = 0
        for phrase in old_key_phrases:
            if str(old_key_phrases[i]).lower() != str(english_key_phrases[i]).lower():
                print(old_key_phrases[i] + " - " + english_key_phrases[i])
            i = i + 1
