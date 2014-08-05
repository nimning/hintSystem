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

App.controller('SetCtrl', function($scope, $location, $window, $routeParams,
                                   WebworkService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    WebworkService.problems($scope.course, $scope.set_id, function(data){
        $scope.problems = data;
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
