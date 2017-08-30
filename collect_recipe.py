import requests
import json
from pymongo import MongoClient
import time
import datetime
from sys import argv

edamam_search_endpoint = 'https://api.edamam.com/search'

with open('/home/cameron/apis/access/edamam.json') as f:
    cred = json.load(f)
    eda_id = cred["app_id"]
    eda_key = cred["API_key"]

def querry_edamam(params):
    """
    send get request to edamam api with given parameters (see
    developer.edamam.com/edamam-docs-recipe-api)
    returns entire json of querry results
    """
    r = requests.get(edamam_search_endpoint, params=params)
    r.raise_for_status()
    return r.json()

def populate_db(search_term, pos_from, pos_to, db):
    """
    querries edamam api with search_term add (pos_to - 1) results to db
    """

    params = {"q": search_term,
              "app_id": eda_id,
              "app_key": eda_key}
    log_f = open('edamam_db_log.log', 'a')

    # Get 100 results at a time
    starts = xrange(pos_from, pos_to, 100)
    for start in starts:
    # request next 100 results and insert into db collection "edamam_recipes"
        params['from'] = start
        params['to'] = start + 100
        hits = querry_edamam(params)['hits']
        if len(hits) == 0:
            raise(Exception("no hits"))
            break
        for hit in hits:
            db["edamam_recipes"].insert_one(hit['recipe'])
        #update log and print status
        message = "inserted results {}-{} for search term '{}' to recipes.edamam_recipes".format(
            params['from'],
            params['to'] - 1,
            search_term)
        ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        with open('edamam_db_log.log', 'a') as log_f:
            log_f.write(ts + ": " + message + "\n")
        print message
        if start + 100 < pos_to:
            print "waiting 5 min for next request"
            time.sleep(301)
        else:
            print "done"




if __name__ == "__main__":
    if len(argv) != 4:
        raise Exception("arguments must be: search_term, from, to")
    client = MongoClient()
    recipes_db = client['recipes']
    search_term, pos_from, pos_to = argv[1:]
    # print search_term, pos_from, pos_to
    populate_db(search_term, int(pos_from), int(pos_to), db=recipes_db)
