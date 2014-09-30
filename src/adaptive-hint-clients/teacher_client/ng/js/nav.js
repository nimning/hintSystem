var App = angular.module('ta-console');

App.controller('NavBarCtrl', function ($scope, $rootScope, $http, $window,
                                       Session, CurrentCourse, AuthService, AUTH_EVENTS) {
    $scope.courses = ["UCSD_CSE103", "CSE103_Fall14"];

    $scope.user_id = Session.user_id;
    $scope.current_course = CurrentCourse;
    $scope.logged_in = Session.logged_in();

    $rootScope.$on(AUTH_EVENTS.loginSuccess, function(event){
        $scope.logged_in = true;
        $scope.user_id = Session.user_id;
    });

    $rootScope.$on(AUTH_EVENTS.logoutSuccess, function(event){
        $scope.logged_in = false;
        $scope.user_id="";
    });

    $scope.logout = function(){
        AuthService.logOut();
    };
});
