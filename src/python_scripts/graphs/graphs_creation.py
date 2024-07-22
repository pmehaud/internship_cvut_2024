#=======================#
# Libraries importation #
#=======================#

import networkx as nx # type: ignore
from pandas import DataFrame
from scipy.spatial import Delaunay # type: ignore
from itertools import combinations
from sklearn.neighbors import NearestNeighbors
from numpy import sqrt, sum

#=======================================================#
# Creation of a graph based on a delaunay triangulation #
#=======================================================#

def delaunay_graph(df: DataFrame) -> tuple[nx.Graph, dict]:
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
    points_pos = df[['latitude', 'longitude']].values

    delaunay_triangulation = Delaunay(points_pos)

    G = nx.Graph()
    nodes = range(len(delaunay_triangulation.points))
    G.add_nodes_from(nodes)

    for simplex in delaunay_triangulation.simplices:
        G.add_edges_from(combinations(simplex, 2))

    G = nx.relabel_nodes(G, dict(zip(nodes, df.index))) # renaming nodes according to the indexes of the dataframe

    pos = dict(zip(df.index, points_pos)) # gives each node his own position

    return G, pos

#=================================================================#
# Creation of the gabriel graph based on a delaunay triangulation #
#=================================================================#

def gabriel_graph(df: DataFrame) -> tuple[nx.Graph, dict]:
    """ Returns a Gabriel Graph based on the Delaunay triangulation and the position of each node.
        
        Parameters
        ----------
        df : DataFrame
            The pandas DataFrame of your data.

        Returns
        -------
        G : Graph
            A Gabriel Graph.
        pos : dict
            The position of G's nodes.
    """
    G, pos = delaunay_graph(df)

    coordsXY = df[['x','y']]

    for edge in G.edges:
        pt1 = edge[0]
        pt2 = edge[1]

        middle_point = (coordsXY.loc[pt1] + coordsXY.loc[pt2])/2

        neigh = NearestNeighbors(radius=sqrt(sum((coordsXY.loc[pt1] - coordsXY.loc[pt2])**2, axis=0))/2)
        neigh.fit(coordsXY)

        if(len(coordsXY.iloc[neigh.radius_neighbors([middle_point], sort_results=True)[1][0][:-2]].index)>0):
            G.remove_edges_from([edge])

    return G, pos