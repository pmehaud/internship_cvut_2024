#=======================#
# Libraries importation #
#=======================#

import networkx as nx # type: ignore
# from pandas import DataFrame # type: ignore
import numpy as np # type: ignore
from scipy.spatial import Delaunay # type: ignore
from itertools import combinations

#=======================================================#
# Creation of a graph based on a delaunay triangulation #
#=======================================================#

def delaunay_graph(df):
    """ Returns a Networkx Graph based on the Delaunay triangulation and the position of each node.
        
        Parameters
        ----------
        df : DataFrame
            The pandas DataFrame of your data.

        Returns
        -------
        G : Graph
            A Networkx Graph graph.
        pos : dict
            The position of G's nodes.
    """
    points_pos = df[['longitude', 'latitude']].values
    
    delaunay_triangulation = Delaunay(points_pos)

    G = nx.Graph()
    nodes = range(len(delaunay_triangulation.points))
    G.add_nodes_from(nodes) # adds nodes names (0 to number_of_points-1)

    for simplex in delaunay_triangulation.simplices:
        G.add_edges_from(combinations(simplex, 2))

    pos = dict(zip(df.index,points_pos)) # gives each node his own position

    return G, pos