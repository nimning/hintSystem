var App = angular.module('ta-console');

App.controller('NavBarCtrl', function ($scope, $http) {
    $scope.courses = ["UCSD_CSE103", "CSE103_Fall14"];
    $scope.current_course = "CSE103_Fall14";
});
