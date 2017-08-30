from feature_building import count_keywords
from pymongo import MongoClient
import re

n = 1000

client = MongoClient()
db = client.recipes
coll = db.eda_cookies
regx = re.compile("cookie", re.IGNORECASE)

keyword_counts = count_keywords(coll.find({"label": regx}))

top_n_keywords = keyword_counts.most_common(n)

f = open('features_1gram.txt', 'a')

for word, count in top_n_keywords:
    input_accepted = False
    while not input_accepted:
        yn = raw_input("keep feature   '{:20}' (count {})?  [y/n]: ".format(word, count))
        if yn == 'y':
            f.write(str(word) + '\n')
            input_accepted = True
        elif yn == 'n':
            input_accepted = True
        else:
            print "chose 'y' or 'n'"

print 'done'
f.close()
