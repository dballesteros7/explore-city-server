var tourer = angular.module('xploreTourer')

tourer.controller('mapCtrl', [ '$scope', '$http', function($scope, $http){
    $scope.map = {
        center : {
            latitude : 47.368620,
            longitude : 8.539891
        },
        zoom : 14,
        control : {}
    };
    $scope.types = new Array();
    $scope.places = new Array();
    $http({
        url : '/api/tourer/types'
    }).success(function(data, status, headers, config){
        data.forEach(function(type){
            $scope.types.push({
                name : type,
                selected : false
            });
        });
    });
    $scope.newQuery = function(){
        $scope.queryId = null;
        $scope.places = [];
    }
    $scope.retrievePlaces = function(){
        var selectedTypes = new Array();
        $scope.types.forEach(function(type){
            if (type.selected) {
                selectedTypes.push(type.name);
            }
        })
        $http({
            url : '/api/tourer/places',
            params : {
                types : JSON.stringify(selectedTypes)
            }
        }).success(function(data, status, headers, config){
            $scope.places = data.places;
            $scope.queryId = data.query_id;
        });
    };
    $scope.drawn = false;
    $scope.drawRadius = function(){
        if (!$scope.drawn) {
            new google.maps.Circle({
                map : $scope.map.control.getGMap(),
                center : new google.maps.LatLng(47.368620, 8.539891),
                radius : 1000
            });
            $scope.drawn = true;
        }
    };
    
    $scope.markerClicked = function($markerModel){
    };
    
    $scope.orienteering = function(){
        $http({
            url : '/api/tourer/crazy',
            params : {
                query_id : $scope.queryId,
            }
        });
    }
} ]);