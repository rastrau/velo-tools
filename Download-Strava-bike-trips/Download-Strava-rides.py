# Python 3.9
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import urllib3
import json
import datetime

# Obtaining client ID, client secret, and refresh token:
# https://www.strava.com/settings/api
payload = {
    'client_id': '<PUT YOUR CLIENT ID HERE>',
    'client_secret': '<PUT YOUR CLIENT SECRET HERE>',
    'refresh_token': '<PUT YOUR REFRESH TOKEN HERE>',
    'grant_type': 'refresh_token',
    'f': 'json'
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
auth_url = 'https://www.strava.com/oauth/token'
# https://developers.strava.com/docs/reference/#api-Activities-getActivityById
activites_url = 'https://www.strava.com/api/v3/athlete/activities'

# Obtaining an access token: 
# https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde
print('Requesting Token...\n')
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print('Access Token = {}\n'.format(access_token))

header = {'Authorization': 'Bearer ' + access_token}
param = {'per_page': 200, 'page': 1}
activities = requests.get(activites_url, headers=header, params=param).json()

records = []
for activity in activities:
    if activity['type'] == 'Ride':                    
        ride_id = activity['id']
        print('Downloading ride %s...' % ride_id)
        ride_url = f'https://www.strava.com/api/v3/activities/{ride_id}/streams?keys=time,latlng,distance,altitude,velocity_smooth,heartrate,cadence,watts,temp&key_by_type=true'
        ride_response = requests.get(ride_url, headers=header)
        ride_data = json.loads(ride_response.text)

        # Convert latlng data to LineString geometry
        latlng = ride_data['latlng']['data']
        coords = [(lng, lat) for lat, lng in latlng]
        geometry = LineString(coords)

    

        # Create GeoDataFrame with ride data
        columns = ['time', 'distance', 'altitude', 'velocity_smooth']
        data = {
            'ride_id': ride_id,
            'start_date_local' : activity['start_date_local'],
            'moving_time': activity['moving_time'],
            'elapsed_time' : activity['elapsed_time'],
            'average_speed': activity['average_speed'],
            'total_elevation_gain' : activity['total_elevation_gain'],
            'elev_high' : activity['elev_high'],
            'elev_low': activity['elev_low']
            }
        data['geometry'] = geometry
        gdf = gpd.GeoDataFrame([data])
        gdf = gdf.set_crs('epsg:4326')
        gdf = gdf.to_crs('epsg:2056')
        
        records.append(gdf)


gdf = pd.concat(records)

# Save GeoDataFrame to geopackage file
filename = 'strava-rides.gpkg'
print('\nSaving in %s...' % filename)
gdf.to_file(filename, 
            layer='strava-rides-until-%s' %
                datetime.datetime.now().strftime('%Y-%m-%d'),
            driver='GPKG')
