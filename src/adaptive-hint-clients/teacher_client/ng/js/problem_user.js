var App = angular.module('ta-console');

App.controller('ProblemUserCtrl', function($scope, $location, $window, $routeParams, $sce, $interval,
                                           WebworkService, SockJSService){
    $scope.course = $routeParams.course;
    $scope.set_id = $routeParams.set_id;
    $scope.problem_id = $routeParams.problem_id;
    $scope.user_id = $routeParams.user_id;
    $scope.student_data = {answers: []};

    var sock = SockJSService.get_sock();
    
    sock.onmessage = function(e) {
	    print("RECIEVED: " + e.data);
	    var data = JSON.parse(e.data);
	    if (data.type == 'student_info') {
	        var student_info = data['arguments'];
            $scope.$apply(function(){
                $scope.pg_file = student_info.pg_file;
                $scope.problem_seed = student_info.pg_seed;
                $scope.student_id = student_info.student_id;
            });
	    }
    };
    SockJSService.teacher_join('teacher', $scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
    SockJSService.request_student($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
    SockJSService.get_student_info($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
    // $interval(function(){
    //     SockJSService.get_student_info($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id);
    // }, 1000);

    // WebworkService.problemPGFile($scope.course, $scope.set_id, $scope.problem_id).success(function(data){
    //     console.log(data);
    //     window.pg_file = data;
    //     $scope.pg_text = data;
    // });

    // WebworkService.problemSeed($scope.course, $scope.set_id, $scope.problem_id, $scope.user_id).success(function(data){
    //     console.log(data);
    //     $scope.problem_seed = data;
    // });

});
