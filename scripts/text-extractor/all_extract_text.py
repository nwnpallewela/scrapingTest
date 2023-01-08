import concurrent
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, wait

import pandas as pd
from lxml.html.clean import Cleaner
import lxml
from boilerpy3 import extractors
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

print(sys.getrecursionlimit())
sys.setrecursionlimit(1500)
print(sys.getrecursionlimit())

# Melbourne 2836, 2837, 3113 3114, 3298, 3299, 3722, 3723, 4156, 4157, 4161 - 4164
# ACT 486, 485, 878. 879, 938, 937, 1020, 1019, 1166, 1167, 1346, 1347,1571, 1572
# sydney 502, 1506,
# brisbane 13023, 13038
# ryde 3486

# genova 2517, 12143
START_PAGE_INDEX = 0
END_PAGE_INDEX = 100000

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

executor = ThreadPoolExecutor(100)


def get_web_page(data_text_l, page_index_1, parent_folder, folder):
    try:
        file_name_1 = "/Users/nuwan/Documents/scrapeData/" + parent_folder + '/' + folder + '/' + \
                      str(page_index_1) + ".html"
        data_text_l.append({"index": index, "url": url, "text": html_file_to_text(file_name_1),
                            "cleaned_text": clean_html_text(file_name_1)})
    except:
        print("An error occurred.")


def download_web_page(url_1, page_index_1, parent_folder, folder):
    try:
        req = Request(url_1, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        save_file_html("/Users/nuwan/Documents/scrapeData/" + parent_folder + '/' + folder, str(page_index_1) + ".html",
                       soup)
    except:
        print("An error occurred.")


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


def save_file_html(folder, name, data):
    if not os.path.exists(folder):
        os.makedirs(folder)
    out_file_name = folder + "/" + name
    out_file = open(out_file_name, "w")
    out_file.write(str(data))
    out_file.close()


def condense_newline(text):
    return '\n'.join([p for p in re.split('\n|\r', text) if len(p) > 0])


def parse_html(html_path):
    # Text extraction with boilerpy3
    html_extractor = extractors.ArticleExtractor()
    return condense_newline(html_extractor.get_content_from_file(html_path))


def clean_html_text(file_name_c):
    cleaned_text = ''
    try:
        cleaned_text = str(lxml.html.tostring(cleaner.clean_html(lxml.html.parse(file_name_c))))
    except:
        print("Error while cleaning data : " + file_name_c)
    return cleaned_text


def html_to_text(folder):
    parsed_texts = []
    file_paths = os.listdir(folder)

    for filepath in file_paths:
        filepath_full = os.path.join(folder, filepath)
        if filepath_full.endswith(".html"):
            try:
                parsed_texts.append(parse_html(filepath_full))
                index = index + 1
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


if __name__ == '__main__':
    f = open('../../configs.json')
    config = json.load(f)
    for i in config['sites']:
        futures = []
        site_urls = []
        urls_file = pd.read_csv("../crawler/files/" + i['parent_folder'] + "/" + i['folder'] + "/site_urls.csv")
        for i_l, row in urls_file.iterrows():
            site_urls.append(row)
        max_count = min(END_PAGE_INDEX, len(site_urls))

        if i.get('actions').get('download_pages') != 'completed':
            index = START_PAGE_INDEX
            os.makedirs('/Users/nuwan/Documents/scrapeData/' + i['parent_folder'] + "/" + i['folder'])
            print(i['parent_folder'] + "/" + i['folder'])
            while index <= max_count and len(site_urls) > index:
                url = site_urls[index]['url']
                page_index = site_urls[index]['page']
                if len(futures) > 50:
                    done, not_done = wait(futures, return_when=concurrent.futures.ALL_COMPLETED,timeout=120)
                    futures = []
                    # get_web_page(url, page_index)
                future = executor.submit(download_web_page, url, page_index, i['parent_folder'], i['folder'])
                futures.append(future)
                index = index + 1
                print(str(index) + '/' + str(max_count))

        if i.get('actions').get('extract_text') != 'completed':
            data_text = []
            index = START_PAGE_INDEX
            while index <= max_count and len(site_urls) > index:
                url = site_urls[index]['url']
                page_index = site_urls[index]['page']
                get_web_page(data_text, page_index, i['parent_folder'], i['folder'])
                index = index + 1
                print(str(index) + '/' + str(max_count))
            df_l = pd.DataFrame(data=data_text)
            df_l = df_l.applymap(lambda x: x.encode('unicode_escape').
                                 decode('utf-8') if isinstance(x, str) else x)
            try:
                with pd.ExcelWriter('files/webPagesExtractedTexts_'+i['folder']+'.xlsx', mode='w') as writer:
                    df_l.to_excel(writer, sheet_name=i['folder'])
            except Exception as e:
                print(e)
    print("End!!!")
