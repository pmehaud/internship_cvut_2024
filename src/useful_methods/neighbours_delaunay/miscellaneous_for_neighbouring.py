#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
from geopy import distance # type: ignore
import pandas as pd # type: ignore
from sklearn.cluster import HDBSCAN # type: ignore
import networkx as nx # type: ignore


#=================#
# Helpful methods #
#=================#

def km_distance(pt1: list, pt2: list) -> float:
    """ Computes the distance in km between pt1 and pt2.
        
        Parameters
        ----------
        pt1, pt2 : list
            The ['latitude', 'longitude'] coordinates of the points.

        Returns
        -------
        km_distance : float
            The distance in km between pt1 and pt2.
    """
    return distance.distance(pt1, pt2).km

def compute_angles(ref_point: int, adj: list, pos: dict) -> np.array:
    """ Computes the angle position of ref_point's neighbours.
        
        Parameters
        ----------
        ref_point : int
            The reference of the central point.
        adj : list
            An array containing references of ref_point's adjacent nodes.
        pos : dict
            A dictionnary referencing all points' positions.

        Returns
        -------
        angles : np.array
            The angle position of ref_point's neighbours (from 0 to 360°).
    """
    angles = []
    for neighbour in adj:
        x_neighbour = pos[neighbour][0]
        y_neighbour = pos[neighbour][1]

        angles.append(np.degrees(np.arctan2(y_neighbour - pos[ref_point][1], x_neighbour - pos[ref_point][0])))
    angles = [round((k + 360) % 360) for k in angles]

    return np.array(angles)

def create_6_quadrants(ref_point: int, adj: list, pos: dict) -> dict:
    """ Creates 6 quadrants around ref_point.
        
        Parameters
        ----------
        ref_point : int
            The reference of the central point.
        adj : list
            An array containing references of ref_point's adjacent nodes.
        pos : dict
            A dictionnary referencing all points' positions.

        Returns
        -------
        quadrants : dict
            A dictionnary referencing in which quadrant adj's point are.
    """
    angles = compute_angles(ref_point, adj, pos)

    quadrants = dict()
    for ind in range(0, 301, 60):
        quadrants[f"{ind}_{ind+60}"] = [adj[k] for k in np.where((angles >= ind) & (angles < ind + 60))[0]] # to have the real name of the node

    return quadrants

def nearestNeighbour(ref_point: int, adj: list, pos: dict) -> int:
    """ Gives the nearest neighbour around ref_point.
        
        Parameters
        ----------
        ref_point : int
            The reference of the central point.
        adj : list
            An array containing references of ref_point's adjacent nodes.
        pos : dict
            A dictionnary referencing all points' positions.

        Returns
        -------
        nearestNeighbour : int
            The reference of the nearest adjacent node, if adj is empty it returns ref_point.
    """
    min = np.inf
    nearestNeighbour = ref_point
    
    for pt2 in adj:
        dist = km_distance(pos[ref_point], pos[pt2])
        if((dist > 0) and (dist < min)):
            min = dist
            nearestNeighbour = pt2

    return nearestNeighbour

def angle_elim(G: nx.Graph, pos: dict, ref_point: int, adj: list, id: int, next_id: int):
    """ Computes the angle elimination for angle criteria (keeps the nearest point).
        
        Parameters
        ----------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
        ref_point : int
            The reference of the central point.
        adj : list
            An array containing references of ref_point's adjacent nodes.
        id, next_id : int
            The indices of the adjacent nodes ind adj.
    """
    if(km_distance(pos[ref_point], pos[adj[id]]) > km_distance(pos[ref_point], pos[adj[next_id]])):
        G.remove_edges_from([(ref_point, adj[id])])
    else:
        G.remove_edges_from([(ref_point, adj[next_id])])

# returns the probability of base stations' city-ness
def probaCity(coordsXY: list) -> pd.Series:
    """ Computes the probability of base stations' city-ness using H-DBScan.
        
        Parameters
        ----------
        coordsXY : list
            [x, y] coordinates of all points (lambert-93 projection).

        Returns
        -------
        probaCity : pd.Series
            A Series containing the probability of base stations' city-ness.
    """
    clusterer = HDBSCAN(min_cluster_size=5, min_samples=40)
    clusterer.fit(coordsXY)

    return pd.Series(data=clusterer.probabilities_, index=coordsXY.index)