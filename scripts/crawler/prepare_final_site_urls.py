import pandas as pd
import os

AUS_DIRS_PATH = "files/aus/"
ITALIAN_DIRS_PATH = "files/italy/"

if __name__ == '__main__':
    aus_dirs = os.listdir(AUS_DIRS_PATH)
    italian_dirs = os.listdir(ITALIAN_DIRS_PATH)
    all_sites = []
    for dirs in [[aus_dirs, AUS_DIRS_PATH, 1], [italian_dirs, ITALIAN_DIRS_PATH, 2]]:
        for directory in dirs[0]:
            if not directory.__contains__("."):
                csv_file = dirs[1] + directory + '/site_urls.csv'
                site_urls = pd.read_csv(csv_file)
                for index, row in site_urls.iterrows():
                    all_sites.append({'council': row['council'], 'page_id': str(row['council']) + '_' + str(row['page']),
                                      'url': row['url'], 'country': dirs[2]})
    all_sites_pd = pd.DataFrame(data=all_sites)
    all_sites_pd.to_csv('files/all_site_urls.csv')
    print('Done')
