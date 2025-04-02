import osmnx as ox
import pyvista as pv
import numpy as np 
import random
from pathlib import Path
from shapely.geometry import Polygon,MultiPolygon

import matplotlib.pyplot as plt
def extrude_buildings(footprints):
    # Create empty PyVista mesh for the final city
    city_mesh = pv.PolyData()
    instances_building = []

    for footprint in footprints:
        # Get coordinates from footprint
        coords = np.array(footprint.exterior.coords)

        # Generate random building height (between 10 and 50 meters)
        height = random.uniform(10, 50)

        # Create watertight building geometry
        points, faces = create_watertight_building(coords, height)

        # Create building mesh
        building = pv.PolyData(points, np.array(faces))

        # Generate and apply random color
        color = generate_random_color()
        building['color'] = np.tile(color, (building.n_points, 1))
        instances_building.append(building)

        # Add to city mesh
        if city_mesh.n_points == 0:
            city_mesh = building
        else:
            city_mesh = city_mesh.merge(building, merge_points=False)

    print("Building extrusion complete")
    return city_mesh, instances_building

def generate_random_color():
    return [random.random() for _ in range(3)]
def create_watertight_building(coords,height):
    coords=coords[:-1]
    n_points=len(coords)
    # Create points for base and top
    base_points = np.column_stack((coords, np.zeros(len(coords))))
    top_points = np.column_stack((coords, np.full(len(coords), height)))

    # Combine all points
    points = np.vstack((base_points, top_points))

    # Create faces
    faces = []

    # Add base (as triangle fan)
    base_face = [n_points] + list(range(n_points))
    faces.extend(base_face)

    # Add roof (as triangle fan)
    roof_indices = list(range(n_points, n_points * 2))
    roof_face = [n_points] + roof_indices
    faces.extend(roof_face)

    # Add walls (as quads)
    for i in range(n_points):
        next_i = (i + 1) % n_points
        wall_face = [4,  # quad
                    i, next_i,  # bottom points
                    n_points + next_i, n_points + i]  # top points
        faces.extend(wall_face)

    return points, faces

def generate_footprints(buildings):
    """
    Convert GeoDataFrame geometries to Shapely polygons.
    """
    footprints = []

    for geom in buildings.geometry:
        if isinstance(geom, MultiPolygon):
            # Split multipolygons into individual polygons
            footprints.extend(list(geom.geoms))
        elif isinstance(geom, Polygon):
            # Add single polygons
            footprints.append(geom)
        # Skip points and other geometry types

    return footprints

def extract_osm_data(location, radius):

    center_point = ox.geocode(location)

    # Récupération des bâtiments
    buildings = ox.features_from_point(
        center_point,
        tags={'building': True},
        dist=radius
    )

    # Récupération des rues
    streets = ox.graph_from_point(center_point, dist=radius, network_type='drive', simplify=False)

    # Projection des données
    buildings = buildings.to_crs(epsg=2154)
    streets = ox.project_graph(streets)  

    return buildings, streets

location = "france,paris,La place du Tertre"
radius = 400

buildings, streets = extract_osm_data(location, radius)
footprints = generate_footprints(buildings)
mesh, bd_instances = extrude_buildings(footprints)

pl = pv.Plotter(border=False)
pl.add_mesh(mesh, scalars=mesh['color'], cmap="tab20", show_edges=False)
pl.remove_scalar_bar()
pl.show(title='(c) Florent Poux - 3D Tech')

print(buildings)
