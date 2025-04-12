import osmnx as ox

# 📍 Télécharger le réseau routier de Marrakech
G = ox.graph_from_place("Marrakesh, Morocco", network_type='drive')

# 💾 Sauvegarder dans un fichier .graphml
ox.save_graphml(G, "ALLmarrakesh.graphml")

print("✅ Fichier ALLmarrakesh.graphml enregistré avec succès.")
