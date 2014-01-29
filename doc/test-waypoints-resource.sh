#!/bin/bash

# Create a single-waypoint mission.
python ../bin/admin_utils.py create mission --url http://localhost:8080/api --name Test_mission_1 Test_waypoint_1 --image-path ./cab_frontal.jpg --location 47.3781603,8.5480106

# Create another mission from the same waypoint
python ../bin/admin_utils.py create mission --url http://localhost:8080/api --name Test_mission_2 Test_waypoint_1

# Create a lonely waypoint
python ../bin/admin_utils.py create waypoint --url http://localhost:8080/api --name Test_waypoint_2 --image-path ./dominos.jpg --location 47.37845,8.54815

# Test the queries
curl -X GET http://localhost:8080/api/missions
echo 
curl -X GET http://localhost:8080/api/waypoints
echo
echo
exit 0
# Check that we can update a waypoint in both location and image
python ../bin/admin_utils.py update waypoint --url http://localhost:8080/api --name Test_waypoint_1 --image-path ./cab_frontal.jpg --location=-47.3781603,8.5480106

# Check the changes
curl -X GET http://localhost:8080/api/missions
echo
curl -X GET http://localhost:8080/api/waypoints
echo
echo

# Update waypoint, image only
python ../bin/admin_utils.py update waypoint --url http://localhost:8080/api --name Test_waypoint_1 --image-path ./cab_frontal.jpg

# Update waypoint, location only
python ../bin/admin_utils.py update waypoint --url http://localhost:8080/api --name Test_waypoint_2 --location=47.3781603,-8.5480106

# Update mission
python ../bin/admin_utils.py update mission --url http://localhost:8080/api --name Test_mission_2 Test_waypoint_2

# Check the changes
curl -X GET http://localhost:8080/api/missions
echo
curl -X GET http://localhost:8080/api/waypoints
echo
echo

# Delete the waypoints and the missions
#python ../bin/admin_utils.py delete mission --url http://localhost:8080/api --name Test_mission_1
#python ../bin/admin_utils.py delete mission --url http://localhost:8080/api --name Test_mission_2
#python ../bin/admin_utils.py delete waypoint --url http://localhost:8080/api --name Test_waypoint_1
#python ../bin/admin_utils.py delete waypoint --url http://localhost:8080/api --name Test_waypoint_2

# Test the queries
curl -X GET http://localhost:8080/api/missions
echo 
curl -X GET http://localhost:8080/api/waypoints
echo
