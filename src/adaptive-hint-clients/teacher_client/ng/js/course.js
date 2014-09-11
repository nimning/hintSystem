var App = angular.module('ta-console');

App.controller('CourseCtrl', function($scope, $location, $window, $routeParams, $interval,
                                      WebworkService, SockJSService,
                                      DTOptionsBuilder, DTColumnDefBuilder, CurrentCourse){
    $scope.course = $routeParams.course;
    CurrentCourse.name = $scope.course;
    WebworkService.sets($scope.course, function(data){
        $scope.sets = data;
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

});

App.controller('SetCtrl', function($scope, $location, $window, $routeParams, $interval, $timeout,
                                   WebworkService, SockJSService, DTOptionsBuilder, DTColumnDefBuilder){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    WebworkService.problems($scope.course, $scope.set_id).success(function(data){
        $scope.problems = data;
    });

    $scope.unassigned_students = [];
    $scope.displayed_students = [];

    $scope.my_students = [];
    var sock = SockJSService.get_sock();
    sock.onmessage = function(event) {
        print("RECEIVED: " + event.data);
        var data = JSON.parse(event.data);
        if (data.type === "my_students"){
            $scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments;
        }
    };

    // Angular Smart-table is weird about updating the first time
    $timeout(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 500);

    var list_students =$interval(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 1000);


    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

    $scope.$on('$destroy', function(event){
        $interval.cancel(list_students);
    });
});
