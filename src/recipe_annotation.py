import pandas as pd
import numpy as np
from recipe_distance import pair_dist_composite
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

class Recipe(object):

    def __init__(self, recipe_features, key, group=None):
        self.label = recipe_features.pop('label')
        self.total_wgt = recipe_features.pop('total_wgt')
        self.line_text = recipe_features.pop('line_text')
        self.health = recipe_features.pop('health')
        self.per_mass = {i: m for i, m in recipe_features.iteritems() if m > 0}
        self.group = group
        self.key = key

    def __repr__(self):
        return "Recipe({})".format(self.label)

    # def add_to_group(self, group):
    #     self.group = group
    #     self.group.member_keys.add(self.key)
    #     self.group.get_stats()

    def _get_annotations(self):
        """
        creates self.annots atribute, joinable lines of recipe ingreds
        """
        lines = []
        for ingred in sorted(self.per_mass,
            key=(lambda ingred: self.group.stats[ingred]['freq']),
            reverse=True):
            stats = self.group.stats[ingred]
            lines.append(
            "{:16}  |   used in {:3.1f}%  of recipes|".format(
            ingred.upper() + ": {:4.1f}g".format(self.per_mass[ingred] * self.total_wgt),
            stats['freq']*100
            ))
            lines.append(
            "     avg: {:5.1f}g  | range: {:4.1f}g - {:4.1f}g       |  std: {:6.4f}g".format(
                stats['avg']*self.total_wgt,
                stats['min']*self.total_wgt,
                stats['max']*self.total_wgt,
                stats['std']*self.total_wgt
            ))
            lines.append("-"*60)
        self.annots = "\n".join(lines)

    def __str__(self):
        self._get_annotations()
        return self.annots

    def get_typicality_score(self, freq_cos_ratio= 0.5):
        freq_score = np.mean([self.group.stats[ingred]['freq']
                                for ingred in self.per_mass])
        vecs = np.array([[self.per_mass[ingred], self.group.stats[ingred]['avg']]
                    for ingred in self.per_mass]).T
        cos_score = np.dot(vecs[0], vecs[1])/(np.linalg.norm(vecs[0])*np.linalg.norm(vecs[1]))
        self.typ_score = (freq_score * freq_cos_ratio) + (cos_score* (1- freq_cos_ratio))
        return self.typ_score


class RecipeGroup(object):

    def __init__(self, df, member_keys=set()):
        #assuming a DataFrame of %mass by ingred, plus label and total_wgt
        #member_keys are df indices of recipes in group
        self.member_keys = set(member_keys)
        self.df = df
        self.create_members()
        self.dists = None

    def get_dists(self, ratio):
        """
        Takes a ratio of cosine weight to Jaccard weight to use in composite
        distance (range 0-1).
        Use ratio=1 for only cosine, ratio=0 for only Jaccard.
        Returns pair wise distance matrix.
        """
        self.dists = pair_dist_composite(self.df)

    def create_members(self):
        self.members = {key: Recipe(self.df.loc[key].to_dict(),key, self)
            for key in self.member_keys}
        self.get_stats()

    def get_stats(self):
        group_df = self.df.drop(["label", "total_wgt", "line_text", "health"], axis=1).loc[list(self.member_keys)]
        group_df.fillna(0, inplace=True)
        used_ingreds = (group_df > 0).sum(axis=0) > 0
        group_df = group_df.loc[:,used_ingreds]
        self.group_df = group_df
        self.stats = {}
        for ingred in group_df.columns:
            uses = group_df[ingred] > 0
            amounts = group_df[ingred][uses]
            self.stats[ingred] = {'freq': uses.mean(),
                                  'min': amounts.min(),
                                  'max': amounts.max(),
                                  'avg': amounts.mean(),
                                  'var': np.var(np.array(amounts), dtype=np.float64),
                                  'std': np.var(np.array(amounts), dtype=np.float64)}


    def grow_from_center(self, center_recp_key, group_size, **kwargs):
        self.member_keys.add(center_recp_key)
        if self.dists is None:
            self.get_dists(kwargs.get('ratio',0.5))
        # find row in dist matrix corresponding to centeral key
        neighbors_d = self.dists[np.where(self.df.index == center_recp_key)].squeeze()
        print neighbors_d.shape
        # add keys of nearest neighbors to member_keys set
        self.member_keys.update(self.df.index[neighbors_d.argsort()[0:group_size]])
        self.create_members()

    def grow_by_linkage(self, group_size, **kwargs):
        if self.dists is None:
            self.get_dists(kwargs.get('ratio',0.5))
        while len(self.member_keys) < group_size:
            member_idx = self.df.index.isin(self.member_keys)
            max_dists = self.dists[member_idx].max(axis=0)
            max_dists[member_idx] = 1
            self.member_keys.add(self.df.index[max_dists.argmin()])
        self.create_members()

    def show_tnse_plot(self, **kwargs):
        tsne = TSNE(perplexity=30, learning_rate=100.0, metric='precomputed')
        if self.dists is None:
            self.get_dists(kwargs.get('ratio',0.5))
        self.embeded_2d = tsne.fit_transform(self.dists)
        self.group_mask = self.df.index.isin(self.member_keys).astype(int)
        colors = np.array(['b', 'r'])[self.group_mask]
        plt.scatter(self.embeded_2d[:,0], self.embeded_2d[:,1], alpha=0.5, c=colors)
        plt.show()

    def _get_group_description(self):
        ingred_lines = []
        thresholds = [(0, None),
                      (.10, 'uncommon'),
                      (.7, 'common'),
                      (1.0, 'core')]
        for ingred, stat_dict in sorted(self.stats.iteritems(),
                                        key=lambda item: item[1]['freq'],
                                        reverse=True):
            freq = stat_dict['freq']
            if freq <= thresholds[-1][0]:
                ingred_lines.append('{} ingredients:'.format(thresholds.pop()[1]))
            ingred_lines.append('   {}, in {:4.1f}%  of recipes'.format(ingred, freq*100))
        self.desc = '\n'.join(ingred_lines[:24])

    def __str__(self):
        self._get_group_description()
        return self.desc

    def find_typical_recipe(self, freq_cos_ratio=0.5, health_labels=[]):
        best_recp = None
        best_score = 0
        for recipe in self.members.itervalues():
            score = recipe.get_typicality_score(freq_cos_ratio  )
            if score > best_score and np.all(np.isin(health_labels, recipe.health)):
                best_score = score
                best_recp = recipe
        return best_recp
