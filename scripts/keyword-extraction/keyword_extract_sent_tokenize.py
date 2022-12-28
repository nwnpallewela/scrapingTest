import csv
import json

from scripts.utils.progress_bar import print_progress_bar
from yake import yake

ROW_COUNT = 94169


if __name__ == '__main__':
    f = open('../../configs.json')
    config = json.load(f)
    if config.get('enableYake'):
        kw_extractor = yake.KeywordExtractor()
        with open('files/yake_key_words_sent_tokenize.csv', mode='w') as yake_key_words:
            fieldnames = ['Site', 'Page', 'Sent', 'KeyWord', 'Value']
            key_words_writer = csv.DictWriter(yake_key_words, fieldnames=fieldnames)
            key_words_writer.writeheader()
            with open("../pre-processing/files/web_pages_text_sent_token.csv") as web_pages_text_sent_token_file:
                web_pages_text_sent_token_file_reader = csv.DictReader(web_pages_text_sent_token_file)
                count = 0
                for row in web_pages_text_sent_token_file_reader:
                    keywords = kw_extractor.extract_keywords(str(row['text']))
                    print_progress_bar(count, ROW_COUNT, prefix='Keywords Extract Web Page Text    :',
                                       suffix='Complete',
                                       length=50)
                    count = count + 1
                    for word in keywords:
                        key_words_writer.writerow({'Site': row['site'], 'Page': row['page'], 'Sent': row['sent'],
                                                   'KeyWord': word[0], 'Value': word[1]})


