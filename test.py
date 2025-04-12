import osmnx as ox
import networkx as nx
import folium
import os

# Charger le graphe .graphml
G = ox.load_graphml("ALLmarrakesh.graphml")

# Convertir en GeoDataFrames
nodes, edges = ox.graph_to_gdfs(G)
print(edges)