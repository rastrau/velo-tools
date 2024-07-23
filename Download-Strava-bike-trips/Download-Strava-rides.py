# Python 3.12.3
import requests
import urllib3
import json
import time
import os

# Obtaining client ID, client secret, and refresh token:
# https://www.markhneedham.com/blog/2020/12/15/strava-authorization-error-missing-read-permission/
# See also: https://www.strava.com/settings/api and 
# https://developers.strava.com/docs/getting-started/#oauth
payload = {
    'client_id': '<PUT YOUR CLIENT ID HERE>',
    'client_secret': '<PUT YOUR CLIENT SECRET HERE>',
    'refresh_token': '<PUT YOUR REFRESH TOKEN HERE>',
    'grant_type': 'refresh_token',
    'f': 'json',
    'scope': 'activity:read_all'
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
auth_url = 'https://www.strava.com/oauth/token'
activities_url = 'https://www.strava.com/api/v3/athlete/activities'

# Obtaining an access token: 
# See also: https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde
print('\nRequesting Token...\n')
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print('Access Token is: {}\n'.format(access_token))

# Get metadata on all activities (including non-Ride-activities)
header = {'Authorization': 'Bearer ' + access_token}
all_activities = []
params = {'per_page': 200, 'page': 1}
while True:
    activities = requests.get(activities_url, headers=header, params=params).json()
    if len(activities) > 0:
        all_activities.extend(activities)
        params['page'] += 1
    else:
        break

# Filter out Ride activities, get relevant metadata and obtain the data
for activity in all_activities:
    if activity['type'] == 'Ride':
        ride_id = activity['id']

        # Persist the ride metadata
        ride_metadata = {
            'ride_id': ride_id,
            'start_date_local' : activity.get('start_date_local', None),
            'distance' : activity.get('distance', None),
            'achievement_count' : activity.get('achievement_count', None),
            'pr_count' : activity.get('pr_count', None),
            'moving_time': activity.get('moving_time', None),
            'elapsed_time' : activity.get('elapsed_time', None),
            'average_speed': activity.get('average_speed', None),
            'max_speed': activity.get('max_speed', None),
            'average_temp': activity.get('average_temp', None),
            'total_elevation_gain' : activity.get('total_elevation_gain', None),
            'elev_high' : activity.get('elev_high', None),
            'elev_low': activity.get('elev_low', None)
        }
        start_date_local = activity.get('start_date_local', None)
        if start_date_local:
            datestamp = start_date_local.split('T')[0]
        else:
            datestamp = '0000-00-00'

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', '%s-activity-%s-metadata.json' % (datestamp, ride_id))
        with open(file_path, 'w') as f:
            json.dump(ride_metadata, f)

        # Download the tracking data, if not yet downloaded (requires an additional API call and thus depletes the quota)
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', '%s-activity-%s-data.json' % (datestamp, ride_id))
        if not os.path.exists(file_path):
            print('Downloading activity file of ride %s...' % ride_id)
            ride_url = f'https://www.strava.com/api/v3/activities/{ride_id}/streams?keys=time,latlng,distance,altitude,velocity_smooth,heartrate,cadence,watts,temp&key_by_type=true'
            ride_response = requests.get(ride_url, headers=header)
            ride_data = json.loads(ride_response.text)
            if "errors" in ride_data.keys():
                print('An error occurred. Skipping this download. Response from the STRAVA API was: %s' % (ride_data))
            else:
                with open(file_path, 'w') as f:
                    json.dump(ride_data, f)
        else:
            print('Activity file %s already exists. Skipping download.' % file_path)

    time.sleep(0.1)
