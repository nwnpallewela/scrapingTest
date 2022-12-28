import pandas as pd

if __name__ == '__main__':
    aus_sites = pd.read_csv('files/keyphrases.csv')
    italian_sites = pd.read_csv('italian/indexed_italian_keyphrases.csv')
    aus_sites['italian_keyword'] = italian_sites['keyword']
    aus_sites.to_csv('files/all_keyphrases.csv')

    aus_sites = pd.read_csv('files/similar_keyphrases.csv')
    italian_sites = pd.read_csv('italian/similar_italian_keyphrases.csv')
    aus_sites['italian_similar_keyword'] = italian_sites['similar_keyword']
    aus_sites.to_csv('files/all_similar_keyphrases.csv')