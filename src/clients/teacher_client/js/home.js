var App = angular.module('ta-console');

App.controller('HomeCtrl', function($scope, $state, $timeout, CurrentCourse, Session, AUTH_EVENTS){
    $scope.courses = ['UCSD_CSE103', 'CSE103_Fall14', 'CSE103_Fall2015'];
});
