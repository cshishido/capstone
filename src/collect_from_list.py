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

def populate_db(search_list, collection):
    """
    querries edamam api with search_term add (pos_to - 1) results to db
    """

    params = {"app_id": eda_id,
              "app_key": eda_key,
              "from": 0,
              "to": 100}
    last_i = len(search_list)-1
    # Get 100 results at a time
    for i, search_term in enumerate(search_list):
        #request with search_term, insert allmrecipes into db
        params["q"] = search_term
        hits = querry_edamam(params)['hits']
        n_items = len(hits)
        ts = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        if n_items == 0:
            print "no hits for search_term{}".format(search_term)
        for hit in hits:
            recipe = hit['recipe']
            recipe['search_term'] = search_term
            collection.insert_one(hit['recipe'])
        #update log and print status
        message = "inserted {} items for search term '{}' to {}".format(
            n_items,
            search_term,
            collection.full_name)
        with open('edama_queries.log', 'a') as log_f:
            log_f.write(ts + ": " + message + "\n")
        print message
        if i < last_i:
            print "waiting 5 min for next request"
            time.sleep(301)
        else:
            print "done"


if __name__ == "__main__":
    if len(argv) != 3:
        raise Exception("arguments must be: file path of list, collection name")
    filepath, coll_name = argv[1:]
    client = MongoClient()
    recipes_db = client['recipes']
    collection = recipes_db[coll_name]
    with open(filepath, 'r') as f:
        search_list = [term.strip() for term in f]
    print "searching these terms:"
    print search_list
    populate_db(search_list, collection)
