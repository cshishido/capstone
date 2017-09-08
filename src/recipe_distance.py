import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from data_processing import mean_scale_recipes

def recipe_jaccard_pairs(df):
    """
    takes a DataFrame or ndarray of ingredients (no labels or totals)
    returns vector-form pair-wise Jaccard distances
    """
    df_binary = df > 0
    return pdist(df_binary, metric='jaccard')



def pair_dist_composite(df, ratio=0.5):
    """
    Takes a recipe DataFrame of ingredients and ratio of cosine weight to
    Jaccard weight to use in composite distance (range 0-1).
    Use ratio=1 for only cosine, ratio=0 for only Jaccard.
    Returns pair wise distance matrix.
    """
    df_scaled = mean_scale_recipes(df)
    cos_dist = ratio * pdist(df_scaled, metric='cosine')
    jac_dist = (1-ratio) * recipe_jaccard_pairs(df_scaled)
    return squareform(cos_dist + jac_dist)
