import pandas as pd
from sklearn.cluster import HDBSCAN
import numpy as np

def city_detection(coordsXY: list, n_neighbors: int = 4) -> pd.Series:
    """ Computes the probability of base stations' city-ness using H-DBScan.
        
        Parameters
        ----------
        coordsXY : list
            [x, y] coordinates of all points (lambert-93 projection).

        Returns
        -------
        probaCity : pd.Dataframe
            A dataframe containing labels of the clusters, associated probabilities and the distance to the mean distance to the n_neighbors closest neighbors
    """

    clusterer = HDBSCAN(min_cluster_size=5, min_samples=40)
    clusterer.fit(coordsXY)

    data = {'labels' : clusterer.labels_, 'probas' : clusterer.probabilities_}

    return pd.DataFrame(data = data, index = coordsXY.index)