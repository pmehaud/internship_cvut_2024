#=======================#
# Libraries importation #
#=======================#

import pandas as pd # type: ignore
from copy import deepcopy

#==================================#
# Extracting data from a dataframe #
#==================================#

def extract_data(df, provider=None, techno=None, department=None, region=None, min_info=False):
    res = deepcopy(df)

    if(min_info):
        res = res[['nom_op', 'num_site', 'longitude', 'latitude', 'nom_reg', 'nom_dep', 'site_2g', 'site_3g', 'site_4g', 'site_5g']]
    if(provider):
        res = res.loc[res['nom_op'] == provider]
        res = res.drop(columns=['nom_op'])
    if(techno in ['2g', '3g', '4g', '5g']):
        res = res.loc[res[f"site_{techno}"] == 1]
        res = res.drop(columns=[f"site_{techno}"])
    if(department):
        res = res.loc[res['nom_dep'] == department]
        res = res.drop(columns=['nom_dep', 'nom_reg'])
    if(region!=None):
        res = res.loc[res['nom_reg'] == region]
        res = res.drop(columns=['nom_reg'])

    return res
    