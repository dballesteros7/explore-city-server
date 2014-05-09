angular.module('xplore.layout')
  .directive('xploreHeader', ['loginApi', function(loginApi){
    function link(scope, element, attr){
      // This directive implements login functionality
      scope.user = {};
      scope.loadingLoginInfo = true;
      loginApi.getCurrentUser(scope.user).then(function(){
        if(scope.user.status !== undefined){
          scope.loadingLoginInfo = false;
          switch (scope.user.status) {
            case 0:
              // User is registered, show his information
              scope.userLoggedIn = true;
              if(!scope.user.profileImg){
                scope.user.profileImg = '/img/icons/user-default.svg';
              }
              break;
            case 1:
              // User is logged in, but is not registered in the system.
              scope.userRegistrationRequired = true;
              break;
            case 2:
              // User is not logged in.
              scope.userLoginRequired = true;
              break;
          }
        }
      });
      scope.registerUser = function(){
        loginApi.registerCurrentUser(scope.inputUsername)
          .then(function(user){
            console.log(user);
            if(!_.isEmpty(user)){
              scope.user = user;
              if(scope.user.status == 0){
                scope.userRegistrationRequired = false;
                scope.userLoggedIn = true;
                if(!scope.user.profileImg){
                  scope.user.profileImg = '/img/icons/user-default.svg';
                }
              }
            }
          });
      };
    }
    return {
      restrict : 'E',
      templateUrl : '/templates/layout/header.html',
      link : link
    };
  }])
  .directive('xploreFooter', function(){
    return {
      restrict : 'E',
      templateUrl : '/templates/layout/footer.html'
    };
  });