angular.module('xplore.index', [ 'xplore.layout', 'xplore.api', 'ngRoute',
                                 'xplore.index.controllers', 'google-maps',
                                 'xplore.utils.filters', 'dateseries'])
  .config([ '$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider){
      $routeProvider.when('/waypoints', {
        controller : 'WaypointsCtrl',
        templateUrl : '/views/waypoints.html',
      });
    }]);
angular.module('xplore.index.controllers', ['xplore.api', 'xplore.utils']);
angular.module('xplore.layout', ['xplore.api']);
angular.module('xplore.utils', []);
angular.module('xplore.utils.filters', []);
angular.module('xplore.api', []);