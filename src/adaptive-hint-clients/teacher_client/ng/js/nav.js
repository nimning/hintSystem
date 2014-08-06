var App = angular.module('ta-console');

App.controller('NavBarCtrl', function ($scope, $http, $window, $route, $routeParams, CurrentCourse) {
    $scope.courses = ["UCSD_CSE103", "CSE103_Fall14"];

    $scope.current_course = CurrentCourse;
    if ($window.sessionStorage.userId){
        $scope.userId = $window.sessionStorage.userId;
        $scope.loginout = {text: 'Logout', href: '#/'+CurrentCourse.name+'/logout'};
    }else{
        $scope.loginout = {text: 'Login', href: '#/CSE103_Fall14/login'};
        $scope.userId = "Account";
    }
});
