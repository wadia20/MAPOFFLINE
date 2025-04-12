import osmnx as ox
from collections.abc import Iterable

# Charger le graphe
G = ox.load_graphml("ALLmarrakesh.graphml")

# Extraire les arêtes (edges)
_, edges = ox.graph_to_gdfs(G)

# Liste pour stocker les noms de rues
flattened_names = []

# Parcourir les noms de rue
for name in edges['name'].dropna():
    if isinstance(name, Iterable) and not isinstance(name, str):
        # Si c'est une liste (ou tuple), on l'étale
        flattened_names.extend(name)
    else:
        flattened_names.append(name)

# Supprimer les doublons
liste_rues = sorted(set(flattened_names))

# Afficher le résultat
print(f"✅ Nombre total de rues uniques : {len(liste_rues)}")
print("📄 Exemple de noms de rue :")
for rue in liste_rues[:20]:
    print("-", rue)
