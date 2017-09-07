from __future__ import division
from feature_building import count_keyword_123grams, token_pipeline
from nltk.util import ngrams
from collections import defaultdict
import pandas as pd

def keyword_hierarchy(curs, dir_path):
    precedence = {}
    word_counts, bigram_counts, trigram_counts = count_keyword_123grams(curs)
    with open(dir_path + 'features_1gram.txt', 'r') as f1:
        for line in f1:
            keyword = line.strip()
            precedence[keyword] = word_counts[keyword]
    bonus2 = max(precedence.values())
    with open(dir_path + 'features_2gram.txt', 'r') as f2:
        for line in f2:
            bigram = line.strip()
            precedence[bigram] = bigram_counts[bigram] + bonus2
    bonus3 = max(precedence.values())
    with open(dir_path + 'features_3gram.txt', 'r') as f3:
        for line in f3:
            trigram = line.strip()
            precedence[trigram] = trigram_counts[trigram] + bonus3
    return precedence

def identify_ingred(ingred_line, precedence_dict, from_url="unknow_url", verbose=False):
    tokens = token_pipeline(ingred_line['text'])
    bigrams = {" ".join(gram) for gram in ngrams(tokens,2)}
    trigrams = {" ".join(gram) for gram in ngrams(tokens,3)}
    keywords = (bigrams.union(trigrams).union(set(tokens))).intersection(precedence_dict)
    if keywords:
        best_keyword = max(keywords, key=precedence_dict.get)
        return best_keyword, ingred_line['weight']
    else:
        message = "no keyword in line: {}  [from: {} ]".format(" ".join(tokens), from_url)
        with open('unidentified_lines.log', 'w') as log_f:
            log_f.write(message + "\n")
        if verbose:
            print message

def get_recipe_features(recipe_dict, precedence_dict):
    tot = recipe_dict['totalWeight']
    features = defaultdict(float,
                {'label': recipe_dict['label'].lower(),
                'total_wgt': tot,
                'url': recipe_dict['url']})
    for ingred_line in recipe_dict['ingredients']:
        ingred = identify_ingred(ingred_line, precedence_dict, from_url=recipe_dict['url'])
        if ingred:
            features[ingred[0]] += ingred[1]/tot
    return features

def get_recipe_df(coll, regx, dir_path='src/'):
    '''
    takes a pymongo collection handle and a compiled regular expression ands returns
    a featurized pandas DataFrame of all recipes in coll matching regx, percent mass
    by ingredient
    '''
    precedence = keyword_hierarchy(coll.find({'label': regx}), dir_path)
    return pd.DataFrame([get_recipe_features(doc, precedence)
                        for doc in coll.find({'label': regx})]
                    ).set_index('url')
