import warnings

warnings.filterwarnings(action='ignore', category=UserWarning)
import gensim
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt


# matplotlib inline

# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')


def simplify(penn_tag):
    pre = penn_tag[0]
    if pre == 'J':
        return 'a'
    elif pre == 'R':
        return 'r'
    elif pre == 'V':
        return 'v'
    else:
        return 'n'


def preprocess(text):
    stop_words = stopwords.words('english')
    toks = gensim.utils.simple_preprocess(str(text), deacc=True)
    wn = WordNetLemmatizer()
    return [wn.lemmatize(tok, simplify(pos)) for tok, pos in nltk.pos_tag(toks) if tok not in stop_words]


def viz_model(model, modeldict):
    ntopics = model.num_topics
    # top words associated with the resulting topics
    topics = ['Topic {}: {}'.format(t, modeldict[w]) for t in range(ntopics) for w, p in
              model.get_topic_terms(t, topn=1)]
    terms = [modeldict[w] for w in modeldict.keys()]
    fig, ax = plt.subplots()
    ax.imshow(model.get_topics())  # plot the numpy matrix
    ax.set_xticks(modeldict.keys())  # set up the x-axis
    ax.set_xticklabels(terms, rotation=90)
    ax.set_yticks(np.arange(ntopics))  # set up the y-axis
    ax.set_yticklabels(topics)
    plt.show()


def test_eta(eta, dictionary, corp, txt, ntopics, print_topics=True, print_dist=True):
    np.random.seed(42)  # set the random seed for repeatability
    bow = [dictionary.doc2bow(line) for line in corp]  # get the bow-format lines with the set dictionary
    with (np.errstate(divide='ignore')):  # ignore divide-by-zero warnings
        model = gensim.models.ldamodel.LdaModel(
            corpus=bow, id2word=dictionary, num_topics=ntopics,
            random_state=42, chunksize=100, eta=eta,
            eval_every=-1, update_every=1,
            passes=150, alpha='auto', per_word_topics=True)
    # visualize the model term topics
    viz_model(model, dictionary)
    print('Perplexity: {:.2f}'.format(model.log_perplexity(bow)))
    if print_topics:
        # display the top terms for each topic
        for topic in range(ntopics):
            print('Topic {}: {}'.format(topic, [dictionary[w] for w, p in model.get_topic_terms(topic, topn=10)]))
    if print_dist:
        # display the topic probabilities for each document
        for line, bag in zip(txt, bow):
            doc_topics = ['({}, {:.1%})'.format(topic, prob) for topic, prob in model.get_document_topics(bag)]
            # print('{} {}'.format(line, doc_topics))
    return model


def create_eta(priors, etadict, ntopics):
    eta = np.full(shape=(ntopics, len(etadict)), fill_value=1)  # create a (ntopics, nterms) matrix and fill with 1
    for word, topic in priors.items():  # for each word in the list of priors
        keyindex = [index for index, term in etadict.items() if term == word]  # look up the word in the dictionary
        if (len(keyindex) > 0):  # if it's in the dictionary
            eta[topic, keyindex[0]] = 1e7  # put a large number in there
    eta = np.divide(eta, eta.sum(axis=0))  # normalize so that the probabilities sum to 1 over all topics
    return eta
