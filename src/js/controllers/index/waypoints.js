angular.module('xplore.index.controllers')
  .controller('WaypointsCtrl', ['$scope', 'retrieveLocation', 'waypointsApi',
    function($scope, retrieveLocation, waypointsApi){
    // Initialize the main map object
    retrieveLocation(function(position){
      $scope.map.center.latitude = position.coords.latitude;
      $scope.map.center.longitude = position.coords.longitude;
    });
    $scope.map = {
        center : {
          latitude : 47.377455,
          longitude : 8.536715
        },
        zoom : 15,
        draggable : true,
        events : {},
        size : 'col-sm-12'
    };
    $scope.waypoints = [];
    $scope.waypointsMap = {};
    $scope.map.events.idle = function(){
      if($scope.halved){
        $scope.map.center = $scope.oldCenter;
        $scope.halved = false;
      } else {
        var mapBounds = $scope.map.getGMap().getBounds();
        var mapBoundsApi = {
            northEast : {
                latitude : mapBounds.getNorthEast().lat(),
                longitude : mapBounds.getNorthEast().lng()
            },
            southWest : {
              latitude : mapBounds.getSouthWest().lat(),
              longitude : mapBounds.getSouthWest().lng()
            }
        };
        waypointsApi.getWaypointsInBox(mapBoundsApi.northEast,
            mapBoundsApi.southWest).then(function(waypointList){
            $scope.waypoints = waypointList;
            _.each($scope.waypoints, function(waypoint){
              waypoint.icon = '/img/icons/waypoint-base.png';
            });
            $scope.waypointsMap = _.indexBy($scope.waypoints, 'name');
            if($scope.displayWaypoint){
              if($scope.waypointsMap[$scope.displayWaypoint.name]){
                $scope.waypointsMap[$scope.displayWaypoint.name].icon = '/img/icons/waypoint-selected.png';
              } else {
                $scope.map.size = 'col-sm-12';
                $scope.displayWaypointInfo = false;
                $scope.displayWaypoint = undefined;
                $scope.oldCenter = _.clone($scope.map.center);
                $scope.$apply(); //FIXME: This is a dirty solution to the coordination problem
                $scope.halved = true;
                google.maps.event.trigger($scope.map.getGMap(), 'resize');
              }
            }
        });
      }
    };
    $scope.waypointClicked = function($markerModel){
      if($scope.map.size.localeCompare('col-sm-12') === 0){
        $scope.map.size = 'col-sm-6';
        $scope.oldCenter = {latitude : $markerModel.latitude,
                            longitude : $markerModel.longitude};
        $scope.displayWaypointInfo = true;
        $scope.$apply();
        $scope.halved = true;
        google.maps.event.trigger($scope.map.getGMap(), 'resize');
      }
      if($scope.displayWaypoint && $scope.waypointsMap[$scope.displayWaypoint.name]){
        $scope.waypointsMap[$scope.displayWaypoint.name].icon = '/img/icons/waypoint-base.png';
      }
      $scope.displayWaypoint = $markerModel;
      $scope.displayWaypoint.user = {};
      $scope.displayWaypoint.missions = [];
      $scope.displayWaypoint.popularity = [];
      $scope.waypointsMap[$scope.displayWaypoint.name].icon = '/img/icons/waypoint-selected.png';
      waypointsApi.similarWaypoints($scope.displayWaypoint)
        .then(function(similarWaypoints){
        $scope.displayWaypoint.similar = similarWaypoints;
      });
      waypointsApi.waypointInfoForUser($scope.displayWaypoint).then(
          function(userInfo){
          if(userInfo.length && userInfo.length > 0){
            $scope.displayWaypoint.user.completed = true;
          } else {
            $scope.displayWaypoint.user.completed = false;
          }
      });
      waypointsApi.missionsForWaypoint($scope.displayWaypoint).then(
          function(missions){
          $scope.displayWaypoint.missions = missions;
          _.each($scope.displayWaypoint.missions, function(val){
            val.link = '#/missions/' + encodeURIComponent(val.name);
          });
      });
      waypointsApi.waypointPopularity($scope.displayWaypoint).then(
          function(popularity){
          $scope.displayWaypoint.popularity = _.map(popularity, function(val){
            return {value : val.visits,
                    datetime : new Date(val.datetime)};
          });
      });
      $scope.$apply();
    };
}]);