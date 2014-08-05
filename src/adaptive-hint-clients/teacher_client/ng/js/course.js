var App = angular.module('ta-console');

App.controller('CourseCtrl', function($scope, $location, $window, $routeParams,
                                      WebworkService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    WebworkService.sets($scope.course, function(data){
        $scope.sets = data;
        console.log(data);
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];
});
