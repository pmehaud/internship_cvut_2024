#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
import pandas as pd # type: ignore
from tqdm import tqdm # progression bar # type: ignore
from copy import deepcopy
import math

from .miscellaneous_for_neighbouring import *



def compute_distance_to_quadrant(ref_point: int, adj: list, pos: dict, quadrant_angles):
    angles = compute_angles(ref_point, adj, pos)
    closest_quadrant_delimations = [quadrant_angles[np.argmin(abs(quadrant_angles-angle))] for angle in angles]
    distances = [math.dist(pos[ref_point], pos[point]) * math.sin(abs(angle-quadrant_angle)) for angle, quadrant_angle, point in zip(angles, closest_quadrant_delimations, adj)]
    return np.sum(distances)
    

def distance_elim(G, pos, edge, max_distance):
    if(km_distance(pos[edge[0]],pos[edge[1]]) > max_distance):
        G.remove_edges_from([edge])

#===========#
# Criterias #
#===========#

def distance_criteria_enhanced(G, pos, distance_range = {'1': 1, '<1->0.6': 5, '<=0.6->0': 10, '0': 15}):
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

def angle_criteria_enhanced(G, pos, angle_range = {'1': 45, '<1->0.6': 30, '<=0.6->0': 20, '0': 15}):
    """ Removes all the edges of G wich doesn't respect the angle criteria.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        min_angle : int (default=30)
            The minimum accepted angle between two neighbours.

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    modif_G = deepcopy(G)

    cityness_proba = probaCity(pd.DataFrame(data=pos.values(), columns=['lat','long'], index=pos.keys()))

    for node in tqdm(cityness_proba.index, desc="nodes"):
        if(cityness_proba[node] == 0):
            min_angle = angle_range['0']
        elif(cityness_proba[node] == 1):
            min_angle = angle_range['1']
        elif((cityness_proba[node] < 1) and (cityness_proba[node] > 0.6)):
            min_angle = angle_range['<1->0.6']
        elif((cityness_proba[node] <= 0.6) and (cityness_proba[node] > 0)):
            min_angle = angle_range['<=0.6->0']

        neighbours = [edge[1] for edge in modif_G.edges(node)]
        angles = compute_angles(node, neighbours, pos)
        idx_angles = np.argsort(angles) # angle des voisins de node

        for i, id in enumerate(idx_angles):
            if(i < len(idx_angles) - 1):
                next_id = idx_angles[i + 1]
                if((angles[next_id] - angles[id]) <= min_angle):
                    angle_elim(modif_G, pos, node, neighbours, id, next_id)
                
        if(idx_angles.size!=0):
            next_id = idx_angles[-1]
            id = idx_angles[0]
            if((360 - angles[next_id] + angles[id]) <= min_angle):
                angle_elim(modif_G, pos, node, neighbours, id, next_id)
        
    return modif_G