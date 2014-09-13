var App = angular.module('ta-console');

App.controller('HomeCtrl', function($scope, CurrentCourse, Session, AUTH_EVENTS){
    $scope.courses = ['UCSD_CSE103', 'CSE103_Fall14'];
});
