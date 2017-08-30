import json
from pymongo import MongoClient
from collections import Counter
import re
from nltk.util import ngrams
from nltk.stem import RegexpStemmer
from nltk.stem.snowball import SnowballStemmer

# stopwords = {
# 'tbsp',
# 'tablespoon',
# 'tsp',
# 'teaspoon',
# 'cup',
# 'ounce',
# 'oz',
# 'gram',
# 'g',
# 'ground',
# 'large',
# 'at',
# 'chopped',
# 'room',
# 'temperature',
# 'hot',
# 'cold',
# 'softened',
# 'packed',
# '',
# 'of',
# 'a',
# 'about'
# 'for',
# }

with open("stopwords.txt", "r") as f:
    stopwords = {word.strip() for word in f}
    stopwords.add('')

# my_stemmer = RegexpStemmer("(s$)")
my_stemmer = SnowballStemmer("english")

def stem_plurals(words):
    return map(my_stemmer.stem, words)

def filter_stopwords(words):
    return [word for word in words if word not in stopwords]

def tokenize_ingred_line(line):
    return re.findall("(?:[a-zA-Z&])+", line.lower())

def token_pipeline(line):
    return filter_stopwords(stem_plurals(tokenize_ingred_line(line)))

def count_keywords(cursor, keyword_counts=None):
    if not keyword_counts:
        keyword_counts = Counter()
    for doc in cursor:
        lines = doc['ingredients']
        for line in lines:
            keyword_counts.update(
            filter_stopwords(
            stem_plurals(
            tokenize_ingred_line(
                line['text']))))
    return keyword_counts


def count_keyword_ngrams(cursor, n, ngram_counts=None):
    if not ngram_counts:
        ngram_counts = Counter()
    for doc in cursor:
        lines = doc['ingredients']
        for line in lines:
            ngram_counts.update(
            ngrams(
                filter_stopwords(
                stem_plurals(
                tokenize_ingred_line(
                line['text'])))
            , n))
    return ngram_counts

def count_keyword_1and2grams(cursor):
    n1gram_counts = Counter()
    n2gram_counts = Counter()
    for doc in cursor:
        lines = doc['ingredients']
        for line in lines:
            tokens = token_pipeline(line['text'])
            n1gram_counts.update(tokens)
            n2gram_counts.update(ngrams(tokens, 2))
    return n1gram_counts, n2gram_counts
