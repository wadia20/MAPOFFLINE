import os
import requests
import mercantile
from tqdm import tqdm

# Define the bounding box of Marrakech
# (You can adjust to your area of interest)
lat_min, lat_max = 31.60, 31.70
lon_min, lon_max = -8.05, -7.90

# Set zoom levels
zoom_levels = range(17, 20)  # zoom 12 to 16

# Set tile server URL (can be replaced with another one if needed)
tile_server = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

# Local storage directory
output_dir = "ALLtiles"

headers = {
    'User-Agent': 'OfflineTileDownloader/1.0'
}

for z in zoom_levels:
    tiles = list(mercantile.tiles(lon_min, lat_min, lon_max, lat_max, [z]))
    print(f"Downloading zoom level {z}, {len(tiles)} tiles")

    for tile in tqdm(tiles):
        x, y = tile.x, tile.y
        url = tile_server.format(z=z, x=x, y=y)
        path = os.path.join(output_dir, str(z), str(x))
        filename = os.path.join(path, f"{y}.png")

        if os.path.exists(filename):
            continue

        os.makedirs(path, exist_ok=True)

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
            else:
                print(f"Failed to download tile {z}/{x}/{y}")
        except Exception as e:
            print(f"Error downloading {z}/{x}/{y}: {e}")
