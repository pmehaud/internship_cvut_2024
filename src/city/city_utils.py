import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.cluster import DBSCAN
import numpy as np
import folium.features


def city_detection_enhanced(coordsXY: list) -> pd.Series:
    """ Computes the probability of base stations' city-ness using H-DBScan.
        
        Parameters
        ----------
        coordsXY : list
            [x, y] coordinates of all points (lambert-93 projection).
        Returns
        -------
        probaCity : pd.Dataframe
            A dataframe containing labels of the clusters and associated probabilities.
    """

    clusterer = HDBSCAN(min_cluster_size=4, min_samples=7, alpha=10)
    clusterer.fit(coordsXY)

    data = {'labels' : clusterer.labels_, 'probas' : clusterer.probabilities_}

    return pd.DataFrame(data = data, index = coordsXY.index)

def city_detection(coordsXY: list) -> pd.Series:
    """ Computes the probability of base stations' city-ness using H-DBScan.
        
        Parameters
        ----------
        coordsXY : list
            [x, y] coordinates of all points (lambert-93 projection).

        Returns
        -------
        probaCity : pd.Dataframe
            A dataframe containing labels of the clusters.
    """

    clusterer = DBSCAN(eps = 2600, min_samples = 10)
    clusterer.fit(coordsXY)

    data = {'labels' : clusterer.labels_}

    return pd.DataFrame(data = data, index = coordsXY.index)



def city_comparison(labels1, labels2):
    l1 = np.array(labels1)
    l2 = np.array(labels2)
    nb = len(l1)
    a = np.sum((l1 == -1) & (l2 == -1))/nb
    b = np.sum((l1 == -1) & (l2 != -1))/nb
    c = np.sum((l1 != -1) & (l2 == -1))/nb
    d = np.sum((l1 != -1) & (l2 != -1))/nb
    return (a,b,c,d)

def plotMapWithColors(df, countryside, colors, title):
    map = folium.Map(location=np.mean(df[['latitude','longitude']], axis=0), zoom_start=7, tiles="Cartodb Positron")
    points = folium.FeatureGroup(f"Points").add_to(map)

    for bs_id, latitude, longitude in df[['latitude', 'longitude']].itertuples():
        if(bs_id in countryside):
            color = colors[bs_id]
            points.add_child(folium.CircleMarker(location=[latitude, longitude], color=color, radius=1))
        # else:
        #     color = mean_distance_choice(bs_id, mean_distances, mean_distance_params, 'colour')
        #     points.add_child(folium.CircleMarker(location=[latitude, longitude], color=color, radius=1))

    folium.LayerControl().add_to(map)

    map.save(f"../../out/maps/{title}.html")
    return map