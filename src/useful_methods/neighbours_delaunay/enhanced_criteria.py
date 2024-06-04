#=======================#
# Libraries importation #
#=======================#


import numpy as np # type: ignore
import pandas as pd # type: ignore
from tqdm import tqdm # progression bar # type: ignore
from copy import deepcopy
import math
import os
import sys

# Get the current directory of the file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory of 'city' to the sys.path
sys.path.append(os.path.join(current_dir, 'city'))
from .miscellaneous_for_neighbouring import *
from city.city_utils import city_detection_enhanced
    

def distance_elim(G, pos, edge, max_distance):
    if(km_distance(pos[edge[0]],pos[edge[1]]) > max_distance):
        G.remove_edges_from([edge])

#==========#
# Criteria #
#==========#

def distance_criterion_enhanced(G: nx.Graph, pos: dict, distance_range: dict = {'1': 1, '<1->0.6': 7, '<=0.6->0': 10, '0': 15}, **kwargs) -> nx.Graph:
    """ Removes all the edges of G wich are longer than the distance_range.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        distance_range : dict<floats>
            The maximum distance between two connected nodes (in km), according to the city-ness probability.

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    cityness_proba = kwargs.get('cityness_proba', None)
    if(cityness_proba is None):
        cityness_proba = city_detection(pd.DataFrame(data=pos.values(), columns=['lat','long'], index=pos.keys()))['probas']
    
    modif_G = deepcopy(G)
    
    for node in tqdm(pos.keys(), desc="nodes - distance"):
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

def quadrant_criterion_enhanced(G: nx.Graph, pos: dict, k_nn: int = 1) -> nx.Graph:
    """ Removes all the edges of G wich doesn't respect the quadrant criterion.
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        k_nn: int
            How much neighbours you want to keep per quadrant.

        Returns
        -------
        modif_G : Graph
            The modified graph.
    """
    modif_G = deepcopy(G)

    for node in tqdm(pos.keys(), desc="nodes - quadrant"):
        neighbours = [edge[1] for edge in modif_G.edges(node)]
        edges_to_remove = list(modif_G.edges(node))
        quadrants = create_6_quadrants_enhanced(node, neighbours, pos)

        nb_neighbours = 0
        while(nb_neighbours < k_nn):
            for quad in quadrants.values():
                nearest_neighbour = nearestNeighbour(node, quad, pos)
                if(nearest_neighbour != node):
                    edges_to_remove.remove((node, nearest_neighbour)) # removing the nearest neighbour in the quadrant centered on node from the edges to remove
                    quad.remove(nearest_neighbour)
            nb_neighbours += 1
        
        modif_G.remove_edges_from(edges_to_remove)

    return modif_G

def angle_criterion_enhanced(G: nx.Graph, pos: dict, angle_range: dict = {'1': 45, '<1->0.6': 30, '<=0.6->0': 20, '0': 15}, **kwargs) -> nx.Graph:
    """ Removes all the edges of G wich doesn't respect the angle criterion.
        
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
    mean_distances = kwargs.get('mean_distance_to_NN', None)
    if(mean_distances is None):
       mean_distances = mean_distance_to_NN(pd.DataFrame(data=pos.values(), columns=['lat','long'], index=pos.keys()))
    
    modif_G = deepcopy(G)

    for node in tqdm(pos.keys(), desc="nodes - angles"):
        # if(cityness_proba[node] == 0):
        #     min_angle = angle_range['0']
        # elif(cityness_proba[node] == 1):
        #     min_angle = angle_range['1']
        # elif((cityness_proba[node] < 1) and (cityness_proba[node] > 0.6)):
        #     min_angle = angle_range['<1->0.6']
        # elif((cityness_proba[node] <= 0.6) and (cityness_proba[node] > 0)):
        #     min_angle = angle_range['<=0.6->0']

        if(mean_distances[node] <= 1.0):
            min_angle = 40
        elif((mean_distances[node] > 1) and (mean_distances[node] <= 2)):
            min_angle = 30
        elif((mean_distances[node] > 2) and (mean_distances[node] <= 5)):
            min_angle = 25
        elif((mean_distances[node] > 5) and (mean_distances[node] <= 10)):
            min_angle = 15
        elif((mean_distances[node] > 10) and (mean_distances[node] <= 15)):
            min_angle = 10
        else:
            min_angle = 5

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