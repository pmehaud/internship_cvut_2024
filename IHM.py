import customtkinter as ctk
import folium
import pandas as pd
import webbrowser
from sklearn.cluster import DBSCAN
import tkinter as tk

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

def getMap(operateurs, regions, labels, couleurs, couleurFonction, popupFonction, location, zoom_start=8, tiles="Cartodb Positron"):
    map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles)
    df_region = df[df['nom_reg'].isin(regions)]
    df_region_operateurs = df_region[df_region['nom_op'].isin(operateurs)]
    # Add markers for each operator
    for ind, lat, lon, num, op in df_region_operateurs[['latitude', 'longitude', 'num_site', 'nom_op']].itertuples():
        couleur = couleurFonction(ind, lat, lon, num, op)
        map.add_child(folium.RegularPolygonMarker(location=[lat, lon], popup=popupFonction(lat, lon, num, op), color=couleur, fill_opacity=0.2, radius=1.5))

    # Define legend HTML content with colored boxes
    legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white;
                    ">ind
        &nbsp; <strong>Legend</strong> <br>
        '''
    for i in range(len(labels)):
        legend_html += f"\n           &nbsp; <span style='color:{couleurs[i]}'>&#9632;</span> {labels[i]} <br>\n"
    legend_html += '    </div>'
    # Add legend to the map
    map.get_root().html.add_child(folium.Element(legend_html))
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
        elif selected_option == "Villes":
            labels = ['Ville', 'Campagne']
            colors = ["blue", "green"]
            couleurFonction = colorFromCity
            popupFonction = getPopUp

        map_obj = getMap(operateurs=selected_operators, regions=selected_regions, labels=labels, couleurs=colors, couleurFonction=couleurFonction, popupFonction=popupFonction, location=location, zoom_start=5)

        # Save map to HTML file
        map_file = "temp_map.html"
        map_obj.save(map_file)

        # Open the map file in a web browser
        webbrowser.open(map_file)

# Création de la fenêtre principale
window = ctk.CTk()
window.minsize(1200, 1300)  # Taille minimale de la fenêtre
window.maxsize(window.winfo_screenwidth(), window.winfo_screenheight())  # Taille maximale de la fenêtre
window.grid_rowconfigure(0, weight=1)  # Centrer verticalement
window.grid_columnconfigure(0, weight=1)  # Centrer horizontalement

# Titre
title_label = ctk.CTkLabel(window, text="Outil d'affichage de carte de stations de bases Françaises", font=("Helvetica", 40, 'bold'), anchor="center", pady=35, padx=20)
title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Menu déroulant pour les actions
action_options = ["Opérateurs", "Villes"]
action_var = tk.StringVar(window)
action_var.set(action_options[0])  # Valeur par défaut
action_combo_box = ctk.CTkComboBox(window, values=action_options, font=("Helvetica", 25), variable=action_var, width=300, height=90, dropdown_font=("Helvetica", 25))
action_combo_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Layout pour les régions et les opérateurs
selection_frame = ctk.CTkFrame(window)
selection_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# ComboBox pour les régions
region_vars = [tk.IntVar() for _ in range(len(regions))]
region_checkboxes = [ctk.CTkCheckBox(selection_frame, text=region, font=("Helvetica", 25), variable=region_vars[i]) for i, region in enumerate(regions)]
for i, checkbox in enumerate(region_checkboxes):
    checkbox.grid(row=i, column=0, sticky="w", padx=40, pady=10)

# ComboBox pour les opérateurs
operator_vars = [tk.IntVar() for _ in range(len(operators))]
operator_checkboxes = [ctk.CTkCheckBox(selection_frame, text=operator, font=("Helvetica", 25), variable=operator_vars[i]) for i, operator in enumerate(operators)]
for i, checkbox in enumerate(operator_checkboxes):
    checkbox.grid(row=i, column=1, sticky="w", padx=40, pady=10)

# Bouton Afficher
afficher_button = ctk.CTkButton(window, text="Afficher", font=("Helvetica", 30), command=plotMap, height=120, width=800)
afficher_button.grid(row=3, column=0, columnspan=2, padx=10, pady=40)

window.update_idletasks()
window.mainloop()
