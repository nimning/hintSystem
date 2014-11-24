var App = angular.module('ta-console');

App.controller('CourseCtrl', function($scope, $location, $window, $stateParams, $interval,
                                      WebworkService, SockJSService,
                                      DTOptionsBuilder, DTColumnDefBuilder, CurrentCourse){
    $scope.course = $stateParams.course;
    CurrentCourse.name = $scope.course;
    WebworkService.sets($scope.course, function(data){
        $scope.sets = data;
    });

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap().withDisplayLength(25);

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

});

App.controller('SetCtrl', function($scope, $location, $window, $stateParams, $interval, $timeout,
                                   WebworkService, SockJSService, DTOptionsBuilder, DTColumnDefBuilder){
    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    WebworkService.problems($scope.course, $scope.set_id).success(function(data){
        $scope.problems = data;
        for(var i=0; i < $scope.problems.length; i++){
	        var problem = $scope.problems[i];
            WebworkService.problemStatus(course, set_id, problem.problem_id).
                success(function(problem, status){
                    problem.students_completed = status.students_completed;
                    problem.students_attempting = status.students_attempted-status.students_completed;
                    problem.free_students = status.students - status.students_attempted;
                }.bind(problem, problem) );
        }
    });

    $scope.unassigned_students = [];
    $scope.displayed_students = [];

    $scope.my_students = [];
    SockJSService.onMessage(function(event, data) {
        if (data.type === "my_students"){
            $scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments;
        }
    });

    // Angular Smart-table is weird about updating the first time
    $timeout(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 500);

    var list_students =$interval(function(){
        SockJSService.send_command('list_students', {'set_id': $scope.set_id});
    }, 1000);


    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withBootstrap().withDisplayLength(25);

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2),
        DTColumnDefBuilder.newColumnDef(3),
        DTColumnDefBuilder.newColumnDef(4),
        DTColumnDefBuilder.newColumnDef(5)
    ];

    $scope.$on('$destroy', function(event){
        $interval.cancel(list_students);
    });
});
