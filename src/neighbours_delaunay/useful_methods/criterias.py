#=======================#
# Libraries importation #
#=======================#

import math
import numpy as np # type: ignore
import pandas as pd # type: ignore
from tqdm import tqdm # progression bar # type: ignore
import copy

#=================#
# Helpful methods #
#=================#

# for the distance criteria
def km_distance(pt1, pt2):
    """ Computes the distance in km between the points pt1 and pt2 (coordinates longitude, latitude).
        
        Parameters
        ----------
        pt1, pt2 : tuple
            Coordinates of the points.

        Returns
        -------
        distance : float
            Distance between pt1 and pt2.
    """
    R = 6371  # average Earth radius in kilometers
    dlat = math.radians(pt2[1] - pt1[1])
    dlon = math.radians(pt2[0] - pt1[0])
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(pt1[1])) * math.cos(math.radians(pt2[1])) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

# for both quadrant and angle criterias
def compute_angles(ref_point, adj, pos): #ref_point: name of the central point / adj: name of the adjacent nodes
    angles = []
    for neighbour in adj:
        x_neighbour = pos[neighbour][0]
        y_neighbour = pos[neighbour][1]

        angles.append(np.degrees(np.arctan2(y_neighbour - pos[ref_point][1], x_neighbour - pos[ref_point][0])))
    angles = [(k + 360) % 360 for k in angles]

    return np.array(angles)

# for the quadrant criteria
def create_6_quadrants(ref_point, adj, pos):
    angles = compute_angles(ref_point, adj, pos)

    quadrants = dict()
    for ind in range(0, 301, 60):
        quadrants[f"{ind}_{ind+60}"] = [adj[k] for k in np.where((angles >= ind) & (angles < ind + 60))[0]] # to have the real name of the node

    return quadrants

# for both quadrant and angle criterias
def nearestNeighbour(ref_point, neighbours, pos):
    """Si pas de voisin, renvoie le point"""
    min = np.inf
    nearestNeighbour = ref_point
    
    for pt2 in neighbours:
        dist = km_distance(pos[ref_point], pos[pt2])
        if((dist > 0) and (dist < min)):
            min = dist
            nearestNeighbour = pt2

    return nearestNeighbour


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
    modif_G = copy.deepcopy(G)
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
    modif_G = copy.deepcopy(G)
    for node in tqdm(pos.keys(), desc="nodes"):
        quadrants = create_6_quadrants(node, pos)
        NN = set()
        for quad in quadrants.values():
            NN.add(nearestNeighbour(node, quad, pos)) # finding the nearest neighbour in the quadrant centered on node
        for edge in modif_G.edges:
            if((edge[0]==node) and (edge[1] not in NN)):
                modif_G.remove_edges_from([edge])

    return modif_G

def quadrant_criteria_v2(G, pos):
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
    modif_G = copy.deepcopy(G)
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
    modif_G = copy.deepcopy(G)

    for node in tqdm(pos.keys(), desc="nodes"):
        neighbours = [edge[1] for edge in G.edges(node)]
        angles = compute_angles(node, neighbours, pos)
        idx_angles = np.argsort(angles) # angle des voisins de node

        for i, id in enumerate(idx_angles):
            if(i < len(idx_angles) - 1):
                next_id = idx_angles[i + 1]
                if((angles[next_id] - angles[id]) <= min_angle):
                    if(km_distance(pos[node], pos[neighbours[id]]) > km_distance(pos[node], pos[neighbours[next_id]])):
                        modif_G.remove_edges_from([(node, neighbours[id])])
                    else:
                        modif_G.remove_edges_from([(node, neighbours[next_id])])
        
    return modif_G