import pandas as pd

class recipe(object):

    def __init__(self, recipe_features, key, group=None):
        self.label = recipe_features.pop('label')
        self.total_wgt = recipe_features.pop('total_wgt')
        self.per_mass = recipe_features
        self.group = group
        self.key = key

    def add_to_group(self, group):
        self.group = group
        self.group.members.add(self.key)
        self.group.get_stats()

    def get_annotations(self):
        """
        creates self.annots atribute, string of recipe lines with stats
        """
        lines = []
        for ingred in sorted(self.per_mass, key=(lambda ingred: self.group.stats[ingred]['freq'])):
            stats = self.group.stats[ingred]
            lines.append("{:16}  {:5.1f}g, used in {:4.1f}%  of recipes".format(
                ingred, self.per_mass[ingred] * self.total_wgt, stats[0]*100
            ))
            lines.append("    AVG: {:5.1f}, RANGE: {:5.1f}g - {:5.1f}g,  VARIANCE: {:5.1f}".format(
                stats['avg']*self.total_wgt,
                stats['min']*self.total_wgt,
                stats['max']*self.total_wgt,
                stats['var']*self.total_wgt
            ))
        self.annots = "\n".join(lines)

class recipe_group(object):

    def __init__(self, member_keys, df):
        #members is a set of recipe keys
        self.member_keys = member_keys
        self.df = df
        self.create_members()
        self.get_stats()

    def create_members(self):
        self.members = []
        for key in member_keys:
            self.members.append(recipe(self.df.iloc[key].to_dict(),key, self))
            

    def get_stats():
        #assuming a DataFrame where member keys are idx
        group_df = self.df.drop('label', axis=1).iloc[list(self.member_keys)]
        self.stats = {}
        for ingred in group_df.colums:
            uses = group_df[ingred] > 0
            amounts = group_df[ingred][uses]
            ingred_min, ingred_max = amounts.min(), amounts.max()
            ingred_mean, ingred_var = amounts.mean(), amounts.var()
            self.stats[ingred] = {'freq': uses.mean(),
                                  'min': amounts.min(),
                                  'max': amounts.max(),
                                  'avg': amounts.mean(),
                                  'var': amounts.var()}
