import pandas as pd
import os

if __name__ == '__main__':
    aus_sites = pd.read_csv('files/matching_keyphrases.csv')
    italian_sites = pd.read_csv('italian/italian_matching_keyphrases.csv')
    aus_sites['country'] = 1
    italian_sites['country'] = 2
    all_sites = pd.concat([aus_sites, italian_sites], ignore_index=True)
    all_sites.to_csv('files/all_site_matching_keyphrases.csv')

