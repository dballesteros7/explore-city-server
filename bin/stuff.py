import requests

response = requests.get('http://localhost:8080/auth/token', params={'username' : 'Mr. X'})
access_token = response.json()['access_token']
mission_name = ''
response = requests.post('http://localhost:8080/api/missions/%s/start' % 'CAB tour',
                         params={'access_token' : access_token})
mission_progress_id = response.json()['mission_progress_id']
waypoint_name = 'CHN bridge 5'
response = requests.post('http://localhost:8080/api/missions/%s/complete/%s' % (mission_progress_id, waypoint_name),
                         params={'access_token' : access_token})
