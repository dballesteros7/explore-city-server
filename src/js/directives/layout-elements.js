var app = angular.module('layout-elements', []);

app.directive('xploreHeader', function(){
  return {
    restrict : 'E',
    templateUrl : '/templates/layout/header.html'
  };
});

app.directive('xploreFooter', function(){
  return {
    restrict : 'E',
    templateUrl : '/templates/layout/footer.html'
  };
});