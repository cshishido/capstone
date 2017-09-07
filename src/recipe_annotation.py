import pandas as pd
import numpy as np

class Recipe(object):

    def __init__(self, recipe_features, key, group=None):
        self.label = recipe_features.pop('label')
        self.total_wgt = recipe_features.pop('total_wgt')
        self.per_mass = {i: m for i, m in recipe_features.iteritems() if m > 0}
        self.group = group
        self.key = key

    def __repr__(self):
        return "Recipe({})".format(self.label)

    def add_to_group(self, group):
        self.group = group
        self.group.members.add(self.key)
        self.group.get_stats()

    def get_annotations(self):
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

class RecipeGroup(object):

    def __init__(self, member_keys, df):
        #assuming a DataFrame of %mass by ingred, plus label and total_wgt
        #member_keys are df indices of recipes in group
        self.member_keys = member_keys
        self.df = df
        self.create_members()
        self.get_stats()

    def create_members(self):
        self.members = {key: Recipe(self.df.loc[key].to_dict(),key, self)
            for key in self.member_keys}

    def get_stats(self):
        group_df = self.df.drop(["label", "total_wgt"], axis=1).loc[list(self.member_keys)]
        group_df.fillna(0, inplace=True)
        used_ingreds = (group_df > 0).sum(axis=0) > 0
        group_df = group_df.loc[:,used_ingreds]
        self.stats = {}
        for ingred in group_df.columns:
            uses = group_df[ingred] > 0
            amounts = group_df[ingred][uses]
            # ingred_min, ingred_max = amounts.min(), amounts.max()
            # ingred_mean, ingred_var = amounts.mean(), amounts.var()
            self.stats[ingred] = {'freq': uses.mean(),
                                  'min': amounts.min(),
                                  'max': amounts.max(),
                                  'avg': amounts.mean(),
                                  'var': np.var(np.array(amounts), dtype=np.float64),
                                  'std': np.var(np.array(amounts), dtype=np.float64)}
