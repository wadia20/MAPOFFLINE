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





def save_to_obj(mesh,output_path):
    output_dir=Path(output_path).parent
    output_dir.mkdir(parents=True,exist_ok=True)
    print("saving model to {output_path}")
    mesh.save(output_path)
    print("export complete")

def streetGraph_to_pyvista(st_graph):
    # Convert the graph to a dataframe
    nodes, edges = ox.graph_to_gdfs(st_graph)

    edges = edges.dropna(subset=['geometry'])

    # Convert geometries to 3D points (z = 0)
    pts_list = edges['geometry'].apply(lambda g: np.column_stack(
        (g.xy[0], g.xy[1], np.zeros(len(g.xy[0])))
    )).tolist()

   

   
    vertices = np.concatenate(pts_list)

    lines = []  # Create an empty array with 3 columns

    j = 0

    for i in range(len(pts_list)):
        pts = pts_list[i]
        vertex_length = len(pts)
        vertex_start = j
        vertex_end = j + vertex_length - 1
        vertex_arr = [vertex_length] \
            + list(range(vertex_start, vertex_end + 1))
        lines.append(vertex_arr)
        j += vertex_length
    print("done")
    return pv.PolyData(vertices, lines=np.hstack(lines))
 
def cloudgify(location, mesh, street_mesh, file_path):
    pl = pv.Plotter(off_screen=True, image_scale=1)
    pl.background_color = 'k'
    actor = pl.add_text(
        location,
        position='upper_left',
        color='lightgrey',
        shadow=True,
        font_size=26,
    )

    pl.add_mesh(mesh, scalars=mesh['color'], cmap="tab20", show_edges=False)
    pl.add_mesh(street_mesh)
    pl.remove_scalar_bar()
    # pl.background_color = 'k'
    # pl.enable_eye_dome_lighting()
    pl.show(auto_close=False)

    viewup = [0, 0, 1]

    # Create output directory if it doesn't exist
    output_dir = Path(file_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = pl.generate_orbital_path(n_points=40, shift=mesh.length, viewup=viewup, factor=3.0)
    pl.open_gif(output_dir/"model.gif")
    pl.orbit_on_path(path, write_frames=True, viewup=viewup)
    pl.close()

    print("Export of GIF successful")
    return

#main
#%% 8. Single Location Experiment
location = "Aachen, Germany"
radius = 500

buildings, streets = extract_osm_data(location, radius)
footprints = generate_footprints(buildings)
mesh, bd_instances = extrude_buildings(footprints)
street_mesh = streetGraph_to_pyvista(streets)
pl = pv.Plotter(border=False)
pl.add_mesh(mesh, scalars=mesh['color'], cmap="tab20", show_edges=False)
pl.remove_scalar_bar()
pl.show(title='(c) Florent Poux - 3D Tech')

output_dir = "output/" + location.split(",")[0]
cloudgify(location, mesh, street_mesh, output_dir)

output_file = output_dir + "/buildings.obj"
output_streets = output_dir + "/streets.obj"
save_to_obj(mesh, output_file)
save_to_obj(street_mesh, output_streets)
