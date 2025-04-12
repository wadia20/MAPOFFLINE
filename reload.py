import osmnx as ox
import folium
import os

# Load the graph
G = ox.load_graphml("ALLmarrakesh.graphml")
nodes, edges = ox.graph_to_gdfs(G)

# Get the center of the graph
center = [nodes.geometry.y.mean(), nodes.geometry.x.mean()]

# Initialize Folium map without base tiles
m = folium.Map(location=center, zoom_start=15, tiles=None)

# Add custom local tiles (served via localhost)
folium.TileLayer(
    tiles="http://localhost:8000/{z}/{x}/{y}.png",
    attr="Offline Tiles",
    name="Offline Map",
    overlay=False,
    control=True
).add_to(m)

# Add edges (roads)
for _, row in edges.iterrows():
    if row.geometry.geom_type == 'LineString':
        coords = [(lat, lon) for lon, lat in row.geometry.coords]
        folium.PolyLine(coords, color="blue", weight=2).add_to(m)

# Add nodes (optional)
for _, row in nodes.iterrows():
    folium.CircleMarker(
        location=(row.geometry.y, row.geometry.x),
        radius=2,
        color="red",
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

# Save to HTML
m.save("zoommap.html")
print("✅ Map saved as offline_map.html. Open it in your browser!")

