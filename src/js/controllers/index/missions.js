angular
    .module('xplore.index.controllers')
    .controller(
        'MissionsCtrl',
        [
            '$scope',
            '$location',
            '$routeParams',
            'missionsApi',
            function($scope, $location, $routeParams, missionsApi){
              $scope.allMissions = [];
              $scope.selectedMission = {
                selectedWaypoint : {}
              };
              $scope.selectedMission.name = $routeParams.mission;
              if ($scope.selectedMission.name) {
                missionsApi
                    .detailedMission($scope.selectedMission.name)
                    .then(
                        function(data){
                          $scope.selectedMission = data.missions[0];
                          $scope.selectedMission.selectedWaypoint = $scope.selectedMission.waypoints[0];
                        });
              }
              missionsApi.missions().then(function(data){
                $scope.allMissions = data.missions;
              });
              $scope.displayMission = function(mission){
                $location.path('/missions/' + encodeURIComponent(mission.name));
              };
              $scope.displayWaypoint = function(waypoint){
                $scope.selectedMission.selectedWaypoint = waypoint;
              };
            } ]);