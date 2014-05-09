angular.module('xplore.utils.filters')
  .filter('stringList', function(){
    return function(stringList){
      if(stringList && stringList.join){
        return stringList.join();
      } else {
        return '';
      }
    };
  });