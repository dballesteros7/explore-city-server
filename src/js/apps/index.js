var app = angular.module('index', [ 'layout-elements', 'ngRoute' ]);

app.config([ '$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider){
      $routeProvider.when('/home/missions', {
        templateUrl : '/templates/missions-collection.html',
      });
      $locationProvider.html5Mode(true);
    } ]);