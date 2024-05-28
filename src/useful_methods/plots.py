#=======================#
# Libraries importation #
#=======================#

import matplotlib.pyplot as plt # type: ignore
import networkx as nx # type: ignore

#==================#
# Global variables #
#==================#

EDGE_COLOR = "lightblue"
NODE_COLOR = "green"

#=====================#
# Plotting parameters #
#=====================#

def plot_params(title, ax, long_points, lat_points):
    """ Sets the right parameters for subplots axes.
        
        Parameters
        ----------
        title : string
            Title of the subplot.
        ax : Matplotlib Axes object (default=None)
            Draw the graph in the specified Matplotlib axes.
        long_points : array
            Longitude coordinates of the points.
        lat_points : array
            Latitude coordinates of the points.
    """
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    ax.set_title(title)

    ax.tick_params(
        reset=True,
        top=False,
        right=False
    )
    
    ax.set_xlim(min(long_points)-0.05, max(long_points)+0.05)
    ax.set_ylim(min(lat_points)-0.05, max(lat_points)+0.05)


#=================================#
# Plotting Delaunay triangulation #
#=================================#

def plot_delaunay(delaunay_triangulation, show=True, **kwargs):
    """ Plots a Delaunay triangulation.
        
        Parameters
        ----------
        delaunay_triangulation : Delaunay
            Result of the Delaunay triangulation.
        show : bool (default=True)
            If True, shows the plot.
        ax : Matplotlib Axes object (default=None)
            Draw the graph in the specified Matplotlib axes.
    """
    ax = kwargs.get('ax', plt)

    ax.triplot(delaunay_triangulation.points[:,0], delaunay_triangulation.points[:,1], delaunay_triangulation.simplices, linewidth=1, c=EDGE_COLOR)
    ax.plot(delaunay_triangulation.points[:,0], delaunay_triangulation.points[:,1], 'o', markersize=3, c=NODE_COLOR)
    
    if(ax!=plt):
        plot_params("Delaunay Triangulation", ax, delaunay_triangulation.points[:,0], delaunay_triangulation.points[:,1])
    else:
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.tick_params(
            reset=True,
            top=False,
            right=False)
    if(show):
        plt.show()


#==================#
# Plotting a graph #
#==================#

def plot_graph(G, pos, show=True, **kwargs):
    """ Plots a Networkx Graph.
        
        Parameters
        ----------
        G : Graph
            The Networkx Graph graph you want to plot.
        pos : dict
            The position of G's nodes.
        show : bool (default=True)
            If True, shows the plot.
        ax : Matplotlib Axes object (default=None)
            Draw the graph in the specified Matplotlib axes.
        title : string
            The title of the subplot (works with ax).
    """
    ax = kwargs.get('ax', None)
    title = kwargs.get('title', "Delaunay Graph")

    nx.draw_networkx(G, pos, node_size=10, with_labels=False, node_color=NODE_COLOR, edge_color=EDGE_COLOR, ax=ax)

    if(ax):
        plot_params(title, ax, [pos[k][0] for k in pos], [pos[k][1] for k in pos])
    else:
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.tick_params(
            reset=True,
            top=False,
            right=False)
    if(show):
        plt.show()