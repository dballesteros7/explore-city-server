angular.module('xplore.api')
  .factory('loginApi', ['$http', function($http){
    var api = {};
    api.getCurrentUser = function(result, errorHandler){
      var promise = $http({
        url : '/api/users/me',
        method : 'GET',
      }).success(function(data){
        _.each(data, function(v, k){
          result[k] = v;
        });
      }).error(errorHandler);
      return promise;
    };
    api.registerCurrentUser = function(username){
      var promise = $http({
        url : '/api/users',
        method : 'POST',
        data : JSON.stringify({
          username : username,
          web : true
        }),
        headers : {"Content-Type" : "application/json"}
      }).then(function(httpData){
        if(httpData.status == 201){
          return httpData.data;
        } else {
          return {};
        }
      });
      return promise;
    };
    return api;
  }])
  .factory('waypointsApi', ['$http', function($http){
    var api = {};
    api.getWaypointsInBox = function(necorner, swcorner, maxResults){
      maxResults = maxResults || 1000;
      var promise = $http({
        url : '/api/waypoints',
        method : 'GET',
        params : {nelatitude : necorner.latitude,
                  nelongitude : necorner.longitude,
                  swlatitude : swcorner.latitude,
                  swlongitude : swcorner.longitude,
                  bounding_box : "True",
                  max_results : maxResults}
      }).then(function(httpData){
        if(httpData.status == 200){
          return httpData.data.waypoints;
        }
      });
      return promise;
    };
    api.similarWaypoints = function(waypoint){
      var promise = $http({
        url : '/api/waypoints',
        method : 'GET',
        params : {
          latitude : waypoint.latitude,
          longitude : waypoint.longitude,
          max_distance : 500
        }
      }).then(function(httpData){
        if(httpData.status == 200){
          return httpData.data.waypoints;
        }
      });
      return promise;
    };
    api.waypointInfoForUser = function(waypoint){
      var promise = $http({
        url : '/api/users/me/waypoints/' + waypoint.name,
        method : 'GET'
      }).then(function(httpData){
        if(httpData.status == 200){
          return httpData.data;
        }
      });
      return promise;
    };
    api.missionsForWaypoint = function(waypoint){
      var promise = $http({
        url : '/api/waypoints/' + waypoint.name + '/missions',
        method : 'GET'
      }).then(function(httpData){
        if(httpData.status == 200){
          return httpData.data;
        }
      });
      return promise;
    };
    api.waypointPopularity = function(waypoint){
      var promise = $http({
        url : '/api/waypoints/' + waypoint.name + '/popularity',
        method : 'GET'
      }).then(function(httpData){
        if(httpData.status == 200){
          return httpData.data;
        }
      });
      return promise;
    };
    return api;
  }]);