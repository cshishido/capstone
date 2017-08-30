from feature_building import count_keyword_ngrams
from pymongo import MongoClient
import re

n = 1000

client = MongoClient()
db = client.recipes
coll = db.eda_cookies
regx = re.compile("cookie", re.IGNORECASE)

keyword_counts = count_keyword_ngrams(coll.find({"label": regx}), 2)

top_n_2grams = keyword_counts.most_common(n)

f = open('features_2gram.txt', 'a')

for gram, count in top_n_2grams:
    input_accepted = False
    phrase = " ".join(gram)
    while not input_accepted:
        yn = raw_input("keep feature   '{:20}' (count {})?  [y/n]: ".format(
            phrase, count))
        if yn == 'y':
            f.write(str(phrase) + '\n')
            input_accepted = True
        elif yn == 'n':
            input_accepted = True
        else:
            print "chose 'y' or 'n'"

print 'done'
f.close()
