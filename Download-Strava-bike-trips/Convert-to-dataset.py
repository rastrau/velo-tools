# Python 3.12.3
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import json
import datetime
import time
import os
import glob

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

file_pattern = os.path.join(data_folder, '*-metadata.json')
metadata_files = glob.glob(file_pattern)

all_activities = []

# Iterate through the list of files
for metadata_file in metadata_files:
    print('Processing metadata and data of ride %s' % metadata_file.split('-')[-2])
    
    # Ingest metadata
    with open(metadata_file, 'r') as f:
        ride_metadata = json.loads(f.read())

    # Ingest data
    try:
        data_file = metadata_file.replace('metadata', 'data')
        with open(data_file, 'r') as f:
            ride_data = json.loads(f.read())
    except FileNotFoundError:
        print('Data file not found: %s' % data_file)
        continue
    
    # Create GeoDataFrame with ride data using the metadata
    # and appending the geometry data
    try:
        latlng = ride_data['latlng']['data']
    except:
        print("Lat/lon data not found: ride_data['latlng']['data']. Skipping this activity.")
        continue

    # Convert latlng data to LineString geometry
    coords = [(lng, lat) for lat, lng in latlng]
    geometry = LineString(coords)

    ride_metadata['geometry'] = geometry
    gdf = gpd.GeoDataFrame([ride_metadata])
    gdf = gdf.set_crs('epsg:4326')
    gdf = gdf.to_crs('epsg:2056')
    
    all_activities.append(gdf)

gdf = pd.concat(all_activities)

# Save GeoDataFrame to geopackage file
file_name = 'strava-rides.gpkg'
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__), file_name)
print('\nSaving in %s...' % file_path)
gdf.to_file(file_path, 
            layer='strava-rides-until-%s' %
            datetime.datetime.now().strftime('%Y-%m-%d'),
            driver='GPKG')
 