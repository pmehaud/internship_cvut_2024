#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
import pandas as pd # type: ignore
from tqdm import tqdm # progression bar # type: ignore
from copy import deepcopy

from .miscellaneous_for_neighbouring import *

def distance_elim(G, pos, edge, max_distance):
    if(km_distance(pos[edge[0]],pos[edge[1]]) > max_distance):
        G.remove_edges_from([edge])

#===========#
# Criterias #
#===========#

def distance_criteria_enhanced(G, pos, distance_range = {'1': 1, '<1->0.6': 2.5, '<=0.6->0': 5, '0': 15}):
    """ Removes all the edges of G wich are longer than the distance_range.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        distance_range : list<floats>
            The maximum distance between two connected nodes (in km), according to the city-ness probability.

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    modif_G = deepcopy(G)

    cityness_proba = probaCity(pd.DataFrame(data=pos.values(), columns=['lat','long'], index=pos.keys())) ## Maybe make it like a global variable
    
    for node in tqdm(cityness_proba.index, desc="nodes"):
        if(cityness_proba[node] == 0):
            max_distance = distance_range['0']
        elif(cityness_proba[node] == 1):
            max_distance = distance_range['1']
        elif((cityness_proba[node] < 1) and (cityness_proba[node] > 0.6)):
            max_distance = distance_range['<1->0.6']
        elif((cityness_proba[node] <= 0.6) and (cityness_proba[node] > 0)):
            max_distance = distance_range['<=0.6->0']
        
        for edge in G.edges(node):
            if(km_distance(pos[edge[0]],pos[edge[1]]) > max_distance):
                modif_G.remove_edges_from([edge])

    return modif_G