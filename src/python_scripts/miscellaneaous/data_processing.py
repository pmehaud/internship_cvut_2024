#=======================#
# Libraries importation #
#=======================#

from pandas import DataFrame
from copy import deepcopy

#==================================#
# Extracting data from a dataframe #
#==================================#

def extract_data(df: DataFrame, provider: str = None, techno: str = None, department: str = None, region: str = None, min_info: bool = True) -> DataFrame:
    """ Extracts data from a pandas DataFrame.
        
        Parameters
        ----------
        df : DataFrame
            The pandas DataFrame of your data.
        provider, techno, department, region : str
            The fields you want to select according to df.
        min_info : bool (default=True)
            True if you want to keep only the essential.
            
        Returns
        -------
        res : DataFrame
            The extracted data you asked for.
    """
    res = deepcopy(df)

    if(min_info):
        res = res[['id_station_anfr', 'nom_op', 'x', 'y', 'latitude', 'longitude', 'nom_reg', 'nom_dep', 'nom_com', 'site_2g', 'site_3g', 'site_4g', 'site_5g']]
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
    