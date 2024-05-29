#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
import pandas as pd # type: ignore
from tqdm import tqdm # progression bar # type: ignore
from copy import deepcopy

from miscellaneous_for_neighbouring import *


#===========#
# Criterias #
#===========#

def distance_criteria(G, pos, max_distance=15):
    """ Removes all the edges of G wich are longer than max_distance.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        max_distance : int (default=15)
            The maximum distance between two connected nodes (in km).

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    modif_G = deepcopy(G)
    for edge in tqdm(modif_G.edges, desc="edges"):
        if(km_distance(pos[edge[0]],pos[edge[1]]) > max_distance):
            modif_G.remove_edges_from([edge])

    return modif_G

def quadrant_criteria(G, pos):
    """ Removes all the edges of G wich doesn't respect the quadrant criteria.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    modif_G = deepcopy(G)
    for node in tqdm(pos.keys(), desc="nodes"):
        neighbours = [edge[1] for edge in modif_G.edges(node)]
        edges_to_remove = list(modif_G.edges(node))
        quadrants = create_6_quadrants(node, neighbours, pos)

        for quad in quadrants.values():
            Near = nearestNeighbour(node, quad, pos)
            if(Near!=node):
                edges_to_remove.remove((node, Near)) # removing the nearest neighbour in the quadrant centered on node from the edges to remove
        
        modif_G.remove_edges_from(edges_to_remove)

    return modif_G

def angle_criteria(G, pos, min_angle = 30):
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

    for node in tqdm(pos.keys(), desc="nodes"):
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