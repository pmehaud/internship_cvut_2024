#=======================#
# Libraries importation #
#=======================#

import numpy as np # type: ignore
from geopy import distance # type: ignore
import pandas as pd # type: ignore
import networkx as nx # type: ignore
from sklearn.neighbors import NearestNeighbors # type: ignore
import math

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

def compute_distance_to_quadrant(ref_point: int, adj: list, pos: dict, angles: list, gap: int) -> float:
    """ Computes the sum of the distances of each point to its closest quadrant edge.
        
        Parameters
        ----------
        ref_point : int
            The reference of the central point.
        adj : list
            An array containing references of ref_point's adjacent nodes.
        pos : dict
            A dictionnary referencing all points' positions.
        angles : list
            An array containing angles from ref_point to ref_point's adjacent nodes.
        gap : int
            The angle gap of the quadrant.

        Returns
        -------
        distance : float
            The sum of the distances of each point to its closest quadrant edge.    
    """
    quadrant_angles = [angle + gap for angle in range(0, 301, 60)]
    closest_quadrant_delimations = [quadrant_angles[np.argmin((np.abs((quadrant_angles-angle) % 360)))] for angle in angles]
    distances = [math.dist(pos[ref_point], pos[point]) * math.sin(abs(angle-quadrant_angle)) for angle, quadrant_angle, point in zip(angles, closest_quadrant_delimations, adj)]
    return np.sum(distances)

def create_6_quadrants_enhanced(ref_point: int, adj: list, pos: dict) -> dict:
    """ Creates 6 quadrants around ref_point, with an angle optimized angle gap (quadrant doesn't always start at 0 degrees).
        
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
    gaps = range(0, 60, 5)
    distances = [compute_distance_to_quadrant(ref_point, adj, pos, angles, gap) for gap in gaps]
    selected_gap = gaps[np.argmax(distances)]

    angles = angles + selected_gap
    angles = angles % 360 
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
    """ Computes the angle elimination for angle criterion (keeps the nearest point).
        
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

def mean_distance_to_NN(coordsXY: list, n_neighbours: int = 4) -> pd.Series:
    """ Computes the mean distance to the n_neighbours.
        
        Parameters
        ----------
        coordsXY : list
            [x, y] coordinates of all points (lambert-93 projection).
        n_neighbours : int (default=4)
            Number of nearest neighbours.

        Returns
        -------
        mean_distances : pd.Series
            A Series containing the mean_distances to base stations' nearest neighbours.
    """
    nbrs = NearestNeighbors(n_neighbors=n_neighbours+1, metric='euclidean').fit(coordsXY)  # n_neighbors+1 because considering himself
    #lambda x, y : distance.distance(x[::-1], y[::-1]).km # we use this because less time and precision overall global
    distances, _ = nbrs.kneighbors(coordsXY)
    
    mean_distances = np.mean(distances[:, 1:]/1000, axis=1)  # we exclude the first element (distance to ourself is 0)

    return pd.Series(data=mean_distances, index=coordsXY.index)

def mean_distance_choice(node: int, mean_distances: pd.Series, mean_distance_params: dict, param: str):
    values = [elem[param] for elem in mean_distance_params.values()]
    if(mean_distances[node] <= 1.0):
        return values[0]
    elif((mean_distances[node] > 1) and (mean_distances[node] <= 2)):
        return values[1]
    elif((mean_distances[node] > 2) and (mean_distances[node] <= 5)):
        return values[2]
    elif((mean_distances[node] > 5) and (mean_distances[node] <= 10)):
        return values[3]
    else:
        return values[4]
    
