#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
from geopy import distance # type: ignore
import pandas as pd # type: ignore


#=================#
# Helpful methods #
#=================#

# for the distance criteria
def km_distance(pt1, pt2):
    return distance.distance(pt1[::-1], pt2[::-1]).km

# for both quadrant and angle criterias
def compute_angles(ref_point, adj, pos): #ref_point: name of the central point / adj: name of the adjacent nodes
    angles = []
    for neighbour in adj:
        x_neighbour = pos[neighbour][0]
        y_neighbour = pos[neighbour][1]

        angles.append(np.degrees(np.arctan2(y_neighbour - pos[ref_point][1], x_neighbour - pos[ref_point][0])))
    angles = [round((k + 360) % 360) for k in angles]

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

def angle_elim(G, pos, node, neighbours, id, next_id):
    if(km_distance(pos[node], pos[neighbours[id]]) > km_distance(pos[node], pos[neighbours[next_id]])):
        G.remove_edges_from([(node, neighbours[id])])
    else:
        G.remove_edges_from([(node, neighbours[next_id])])