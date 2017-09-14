from flask import Flask, render_template, request
import pandas as pd
import re
import numpy as np
from pymongo import MongoClient
from src.data_processing import get_recipe_df
from src.recipe_annotation import Recipe, RecipeGroup
from src.recipe_distance import pair_dist_composite
from sklearn.manifold import TSNE

app = Flask(__name__)

client = MongoClient()
db = client['recipes']
coll = db.eda_cookies
cookie_regx = re.compile("cookie", re.IGNORECASE)
df_cookies = get_recipe_df(coll, cookie_regx)
dists = pair_dist_composite(df_cookies)
embeded_2d = TSNE(learning_rate=200, metric='precomputed').fit_transform(dists)

@app.route('/', methods=['GET'])
def main_page():
    return render_template('main_page.html')

@app.route('/result_label', methods=['POST']):
def results_from_label:
    user_data = request.json
    lbl_regx = ".".joing(user_data['in_label'].split())
    grp_keys = df_cookies.index[df_cookies.label.str.contains(lbl_regx, case=False, regex=True)]
    recp_group = RecipeGroup(df_cookies, grp_keys, dists=dists, embeded_2d=embeded_2d)
    return output_json(recp_group)


@app.route('/result_url', methods=['POST']):
def results_from_example:
    user_data = request.json
    recp_group = RecipeGroup(df_cookies, {user_data['in_url']}, dists=dists, embeded_2d=embeded_2d)

def output_json(recp_group):
    group_size = len(recp_group.member_keys)
    group_desc = recp_group.get_d

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
