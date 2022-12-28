from scipy import spatial


def get_spacy_document(text, nlp_o):
    main_doc = nlp_o(text)  # create spacy document object
    return main_doc


# method to find cosine similarity
def cosine_similarity(vector_1, vector_2):
    # return cosine distance
    return 1 - spatial.distance.cosine(vector_1, vector_2)
