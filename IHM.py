import customtkinter as ctk
import folium
import pandas as pd
import webbrowser
from sklearn.cluster import DBSCAN
import tkinter as tk
from scipy.spatial import Voronoi, Delaunay
import numpy as np

ctk.set_default_color_theme("dark-blue")

df = pd.read_csv("database/data.csv", sep=";", decimal=',')
df = df.sample(frac=1).reset_index(drop=True)

# Sample data for regions and operators
operators = df['nom_op'].unique()
regions = df['nom_reg'].unique()

# Default map location
location = [45.5, 4.5]

dbscan = DBSCAN(eps=0.03, min_samples=15).fit(df[['longitude', 'latitude']])
operatorCityLabels = dbscan.labels_

def colorFromOp(ind, lat, lon, num, op):
    match op:
        case 'Orange':
            return '#fc5603'
        case "SFR":
            return '#169e26'
        case 'Bouygues Telecom':
            return '#035afc'
        case 'Free Mobile':
            return '#dbd640'
        case _:
            print(f"couleur associée à l'opérateur {op} non trouvé")
            return '000000'

def colorFromCity(ind, lat, lon, num, op):
    return 'green' if ( operatorCityLabels[ind] == -1) else 'blue'

def getPopUp(lat, lon, num, op):
    return f"Station de base : \n{num}\nOperateur :\n{op}\ncoordonnées :\n({lon}, {lat})"

def getMap(operateurs, regions, labels, couleurs, couleurFonction, popupFonction, location, zoom_start=8, tiles="Cartodb Positron", delaunay=False, voronoi=False):
    map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)

    df_region = df[df['nom_reg'].isin(regions)]      
    df_region_operateurs = df_region[df_region['nom_op'].isin(operateurs)]
    
    if(not(delaunay or voronoi)):
        # add legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white;
                    "><strong>Legend</strong> <br>
        '''
        for i in range(len(labels)):
            legend_html += f"\n           &nbsp; <span style='color:{couleurs[i]}'>&#9632;</span> {labels[i]} <br>\n"
        legend_html += '    </div>'
        map.get_root().html.add_child(folium.Element(legend_html))
    
    # add Voronoi or Delauney edges
    else:
        coords = df_region_operateurs[['latitude', 'longitude']].to_numpy()
        if (delaunay):
            delaunay = Delaunay(coords)
            for simplice in delaunay.simplices:      
                # Create a Folium polygon using the vertices
                vertices = [coords[simplice]]
                folium.Polygon(
                    locations=vertices,
                    color="blue",
                    weight=2,
                    fill_color="cyan",
                    fill_opacity=0.1,
                    fill=True
                ).add_to(map)
        else :
            voronoi = Voronoi(coords)
            for region_index in range(len(voronoi.regions)):
                region = voronoi.regions[region_index]
                if not -1 in region and len(region) > 0:
                    # Extract the vertices of the region
                    vertices = [voronoi.vertices[i] for i in region]
                    
                    # Create a Folium polygon using the vertices
                    folium.Polygon(
                        locations=vertices,
                        color="blue",
                        weight=2,
                        fill_color="cyan",
                        fill_opacity=0.1,
                        fill=True
                    ).add_to(map)
        
    # Add markers for each operator
    for ind, lat, lon, num, op in df_region_operateurs[['latitude', 'longitude', 'num_site', 'nom_op']].itertuples():
        couleur = couleurFonction(ind, lat, lon, num, op)
        map.add_child(folium.RegularPolygonMarker(location=[lat, lon], popup=popupFonction(lat, lon, num, op), color=couleur, fill_opacity=0.2, radius=1.5))
    
    return map

def plotMap():
    # Get selected option
    selected_option = action_var.get()
    if (selected_option in action_options):
        # Get selected operators and regions
        selected_operators = [operators[i] for i in range(len(operators)) if operator_vars[i].get() == 1]
        selected_regions = [regions[i] for i in range(len(regions)) if region_vars[i].get() == 1]

        if selected_option == "Opérateurs":
            labels = selected_operators
            colors = [colorFromOp(0, 0, 0, 0, operator) for operator in selected_operators]
            couleurFonction = colorFromOp
            popupFonction = getPopUp
            delauney = False
            voronoi = False
        elif selected_option == "Villes":
            labels = ['Ville', 'Campagne']
            colors = ["blue", "green"]
            couleurFonction = colorFromCity
            popupFonction = getPopUp
            delauney = False
            voronoi = False
        elif selected_option == "Delauney":
            couleurFonction=lambda ind, lat, lon, num, op : 'black'
            popupFonction=getPopUp
            labels = []
            colors = []
            delauney = True
            voronoi = False
        elif selected_option == "Voronoi":
            couleurFonction=lambda ind, lat, lon, num, op : 'black'
            popupFonction=getPopUp
            labels = []
            colors = []
            delauney = False
            voronoi = True

        map_obj = getMap(operateurs=selected_operators, regions=selected_regions, labels=labels, couleurs=colors, couleurFonction=couleurFonction, popupFonction=popupFonction, location=location, zoom_start=5, delaunay=delauney, voronoi=voronoi)

        # Save map to HTML file
        map_file = "temp_map.html"
        map_obj.save(map_file)

        # Open the map file in a web browser
        webbrowser.open(map_file)

def select_all(variables, select_all_state):
    for var in variables:
        var.set(select_all_state)


# Création de la fenêtre principale
window = ctk.CTk()
window.minsize(1400, 1000)  # Taille minimale de la fenêtre
window.maxsize(2500, 1500)  # Taille maximale de la fenêtre
window.grid_rowconfigure(0, weight=1)  # Centrer verticalement
window.grid_columnconfigure(0, weight=1)  # Centrer horizontalement

# Titre
title_label = ctk.CTkLabel(window, text="Outil d'affichage de carte de stations de bases Françaises", font=("Helvetica", 31, 'bold'), anchor="center", pady=15, padx=20)
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Menu déroulant pour les actions
action_options = ["Opérateurs", "Villes", "Delauney", "Voronoi"]
action_var = tk.StringVar(window)
action_var.set(action_options[0])  # Valeur par défaut
action_combo_box = ctk.CTkComboBox(window, values=action_options, font=("Helvetica", 25), variable=action_var, width=300, height=90, dropdown_font=("Helvetica", 25))
action_combo_box.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Layout pour les régions et les opérateurs
selection_frame = ctk.CTkFrame(window)
selection_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# En tête de colonne pour les régions avec case à cocher pour sélectionner toute la colonne
region_label = ctk.CTkLabel(selection_frame, text="Régions:", font=("Helvetica", 30, 'bold'), anchor="center")
region_label.grid(row=0, column=0, sticky="w", pady=20, padx=10)
region_select_all_var = tk.BooleanVar()
region_select_all_checkbox = ctk.CTkCheckBox(selection_frame, text="Tout sélectionner", font=("Helvetica", 20), variable=region_select_all_var, command=lambda: select_all(region_vars, region_select_all_var.get()))
region_select_all_checkbox.grid(row=0, column=1, sticky="w", pady=20, padx=10)

# ComboBox pour les régions avec case à cocher
region_vars = [tk.IntVar() for _ in range(len(regions))]
region_checkboxes = [ctk.CTkCheckBox(selection_frame, text=region, font=("Helvetica", 25), variable=region_vars[i]) for i, region in enumerate(regions)]
for i, checkbox in enumerate(region_checkboxes):
    checkbox.grid(row=i+1, column=0, sticky="w", padx=40, pady=10)

# En tête de colonne pour les opérateurs avec case à cocher pour sélectionner toute la colonne
operator_label = ctk.CTkLabel(selection_frame, text="Opérateurs:", font=("Helvetica", 30, 'bold'), anchor="center")
operator_label.grid(row=0, column=2, sticky="w", pady=20, padx=10)
operator_select_all_var = tk.BooleanVar()
operator_select_all_checkbox = ctk.CTkCheckBox(selection_frame, text="Tout sélectionner", font=("Helvetica", 20), variable=operator_select_all_var, command=lambda: select_all(operator_vars, operator_select_all_var.get()))
operator_select_all_checkbox.grid(row=0, column=3, sticky="w", pady=20, padx=10)

# ComboBox pour les opérateurs avec case à cocher
operator_vars = [tk.IntVar() for _ in range(len(operators))]
operator_checkboxes = [ctk.CTkCheckBox(selection_frame, text=operator, font=("Helvetica", 25), variable=operator_vars[i]) for i, operator in enumerate(operators)]
for i, checkbox in enumerate(operator_checkboxes):
    checkbox.grid(row=i+1, column=2, sticky="w", padx=40, pady=10)

# Bouton Afficher
afficher_button = ctk.CTkButton(window, text="Afficher", font=("Helvetica", 30), command=plotMap, height=120, width=800)
afficher_button.grid(row=3, column=0, columnspan=3, padx=10, pady=40)

window.update_idletasks()
window.mainloop()