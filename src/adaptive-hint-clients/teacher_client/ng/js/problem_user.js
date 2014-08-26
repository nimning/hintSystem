var App = angular.module('ta-console');

App.controller('ProblemUserCtrl', function($scope, $location, $window, $routeParams, $sce, $interval,
                                           WebworkService, SockJSService){
    var course = $scope.course = $routeParams.course;
    var set_id = $scope.set_id = $routeParams.set_id;
    var problem_id = $scope.problem_id = $routeParams.problem_id;
    var user_id = $scope.user_id = $routeParams.user_id;
    $scope.student_data = {answers: []};

    var sock = SockJSService.get_sock();
    $scope.current_answers = [];
    sock.onmessage = function(e) {
	    print("RECIEVED: " + e.data);
	    var data = JSON.parse(e.data);
	    if (data.type == 'student_info') {
	        var student_info = data['arguments'];
            $scope.$apply(function(){
                $scope.pg_file = student_info.pg_file;
                $scope.problem_seed = student_info.pg_seed;
                $scope.student_id = student_info.student_id;
                $scope.current_answers = student_info.current_answers;
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

    // Auto send 'release_student' when closing window
    $scope.$on('$destroy', function(event){
        SockJSService.release_student(course, set_id, problem_id, user_id);
    });

    window.onbeforeunload = function() {
        SockJSService.release_student(course, set_id, problem_id, user_id);
    };



});
