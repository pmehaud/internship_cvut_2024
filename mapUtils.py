import folium
import pandas as pd
import webbrowser
from sklearn.cluster import DBSCAN
from scipy.spatial import Voronoi, Delaunay
import numpy as np

# Default map location
location = [45.5, 4.5]
zoom_start = 5
tiles = "Cartodb Positron"

def getPopUp(lat, lon, num, op, s2g, s3g, s4g, s5g):
    return f"Station de base : \n{num}\nOperateur :\n{op}\ntechnos : {technosToTxt(s2g, s3g, s4g, s5g)}"

def technosToTxt(s2g, s3g,s4g,s5g):
    return ("2G " if s2g else "") + ("3G " if s3g else "") + ("4G " if s4g else "") + ("5G " if s5g else "")
def addLegend(map, labelsToColors):
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white;
                "><strong>Legend</strong> <br>
    '''
    for label in labelsToColors.keys():
        legend_html += f"\n&nbsp; <span style='color:{labelsToColors.get(label)}'>&#9632;</span> {label} <br>\n"
    legend_html += '</div>'
    map.get_root().html.add_child(folium.Element(legend_html))

def getPointsInfos(data_filtered, option, epsilon, nmin, selected_tech):
    labels = pd.DataFrame(index=data_filtered.index)
    labelsToColors=dict()
    match(option):
        case "Villes":
            dbscan_labels=DBSCAN(eps=epsilon, min_samples=nmin).fit(data_filtered[['longitude', 'latitude']]).labels_
            labels=['Campagne' if ( dbscan_label == -1) else 'Ville' for dbscan_label in dbscan_labels]
            labelsToColors={'Campagne':'green', 'Ville':'blue'}
        case "Opérateurs":
            labels = data_filtered['nom_op']
            labelsToColors={'Orange':'#fc5603','SFR':'#169e26','Bouygues Telecom':'#035afc', 'Free Mobile':'#dbd640'}
        case "Technologies":
            # Créer un DataFrame avec les technologies sélectionnées
            tech_df = data_filtered[selected_tech]

            # Trouver la technologie la plus élevée pour chaque ligne
            highest_tech = tech_df.idxmax(axis=1).apply(lambda x: x.split('_')[1].upper())

            # Remplir labels avec les noms des technologies les plus élevées
            labels = highest_tech

            labelsToColors={"2G":'lime',"3G":'yellow',"4G":'orange', "5G":'red'}
    return (labels,labelsToColors)

            


def getMap(data, selected_providers, selected_regions, selected_technologies, option, epsilon, nmin):
    map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)
    data_filtered = data[data['nom_reg'].isin(selected_regions)]      
    data_filtered = data_filtered[data_filtered['nom_op'].isin(selected_providers)]
    data_filtered = data_filtered[data_filtered[selected_technologies].any(axis=1)]
    # Obtenez les labels et les couleurs correspondantes
    labels, labelsToColors = getPointsInfos(data_filtered, option, epsilon, nmin, selected_technologies)
    
    if(option=="Delaunay" or option == "Voronoi"):
        coords = data_filtered[['latitude', 'longitude']].to_numpy()
        if (option=="Delaunay"):
            delaunay = Delaunay(coords)
            polygons = [coords[simplice] for simplice in delaunay.simplices]
        else:
            polygons = []
            voronoi = Voronoi(coords)
            for region_index in range(len(voronoi.regions)):
                region = voronoi.regions[region_index]
                if not -1 in region and len(region) > 0:
                    # Extract the vertices of the region
                    polygons.append([voronoi.vertices[i] for i in region])

        for polygon in polygons:      
            # Create a Folium polygon
            folium.Polygon(
                locations=polygon,
                color="blue",
                weight=2,
                fill_color="cyan",
                fill_opacity=0.1,
                fill=True
            ).add_to(map)
            
    else:
        addLegend(map, labelsToColors)
    
    
    # Add markers for each provider
    for ind, lat, lon, num, op, s2g, s3g, s4g, s5g in data_filtered[['latitude', 'longitude', 'num_site', 'nom_op', 'site_2g', 'site_3g', 'site_4g','site_5g']].itertuples():
        map.add_child(folium.RegularPolygonMarker(location=[lat, lon], popup=getPopUp(lat, lon, num, op,s2g, s3g, s4g, s5g), color=labelsToColors.get(labels[ind]) if option != "Delaunay" and option != "Voronoi" else 'black', fill_opacity=0.2, radius=1.5))
    
    return map