import osmnx as ox
import networkx as nx
import folium
import os

# Charger le graphe .graphml
G = ox.load_graphml("ALLmarrakesh.graphml")

# Convertir en GeoDataFrames
nodes, edges = ox.graph_to_gdfs(G)

# Définir les noms des rues
start_street = "Avenue Al Markeb"
end_street = "Avenue Antaki"

# Chercher les arêtes correspondantes
start_edges = edges[edges['name'].astype(str).str.contains(start_street, case=False, na=False)]
end_edges = edges[edges['name'].astype(str).str.contains(end_street, case=False, na=False)]

# Vérification
if start_edges.empty:
    print(f"❌ Aucune rue trouvée avec le nom : {start_street}")
    print("Voici quelques noms de rue disponibles :")
    print(edges['name'].dropna().unique()[:20])
    exit()

if end_edges.empty:
    print(f"❌ Aucune rue trouvée avec le nom : {end_street}")
    print("Voici quelques noms de rue disponibles :")
    print(edges['name'].dropna().unique()[:20])
    exit()
# Obtenir un point GPS au milieu d'un segment de chaque rue
start_point = start_edges.iloc[0].geometry.interpolate(0.5, normalized=True)
end_point = end_edges.iloc[0].geometry.interpolate(0.5, normalized=True)

# Trouver les nœuds les plus proches
start_node = ox.distance.nearest_nodes(G, X=start_point.x, Y=start_point.y)
end_node = ox.distance.nearest_nodes(G, X=end_point.x, Y=end_point.y)

# Calculer le plus court chemin en fonction de la distance ('length' en mètres)
shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='length')

# Récupérer les coordonnées du chemin
path_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in shortest_path]

# Centrer la carte autour du chemin
center = path_coords[len(path_coords)//2]

# Initialiser la carte folium sans tuiles de base
m = folium.Map(location=center, zoom_start=15, tiles=None)

# Ajouter les tuiles locales (tileserver en localhost)
folium.TileLayer(
    tiles="http://localhost:8000/{z}/{x}/{y}.png",
    attr="Offline Tiles",
    name="Offline Map",
    overlay=False,
    control=True
).add_to(m)

# Ajouter toutes les routes
for _, row in edges.iterrows():
    if row.geometry.geom_type == 'LineString':
        coords = [(lat, lon) for lon, lat in row.geometry.coords]
        folium.PolyLine(coords, color="blue", weight=2).add_to(m)

# Ajouter les nœuds (optionnel)
for _, row in nodes.iterrows():
    folium.CircleMarker(
        location=(row.geometry.y, row.geometry.x),
        radius=2,
        color="red",
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

# Ajouter le chemin le plus court en vert
folium.PolyLine(path_coords, color="green", weight=5, opacity=0.8, tooltip="Shortest Path").add_to(m)

# Ajouter des marqueurs pour début et fin
folium.Marker(path_coords[0], popup="Départ", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(path_coords[-1], popup="Arrivée", icon=folium.Icon(color='red')).add_to(m)

# Sauvegarder la carte avec le chemin
m.save("zoommappath.html")
print("✅ Carte avec le chemin sauvegardée sous zoommap_with_path.html")
# Obtenir les arêtes (edges) du chemin
edge_list = list(zip(shortest_path[:-1], shortest_path[1:]))

# Extraire les noms de rue des arêtes du chemin
street_names = []
for u, v in edge_list:
    data = G.get_edge_data(u, v)
    if data:
        # Si plusieurs versions (multi-edges), on prend la première
        edge_data = data[list(data.keys())[0]]
        name = edge_data.get('name')
        if name:
            # Si c'est une liste de noms, on les ajoute tous
            if isinstance(name, list):
                street_names.extend(name)
            else:
                street_names.append(name)

# Supprimer les doublons en gardant l’ordre
seen = set()
unique_streets = [x for x in street_names if not (x in seen or seen.add(x))]

# Afficher les noms des rues utilisées dans le chemin
print("🛣️ Rues traversées sur le chemin :")
for street in unique_streets:
    print(" -", street)
