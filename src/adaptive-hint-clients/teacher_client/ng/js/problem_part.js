var App = angular.module('ta-console');

App.controller('ProblemPartCtrl', function($scope, $location, $window, $stateParams,
                                           $sce, $timeout, $interval, $anchorScroll, $modal, $log,
                                           WebworkService, SockJSService, APIHost,
                                           DTOptionsBuilder, DTColumnDefBuilder){

    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    var part_id = $scope.part_id = $stateParams.part_id;
    $scope.input_id = 0;

    $scope.hints = [];
    angular.forEach(hints, function(value, key){
        $scope.hints.push(value);
    });

    WebworkService.answersByPart(course, set_id, problem_id).
        success(function(data){
            var answersByPart = {};
            angular.forEach(data, function(value){
                if (!answersByPart[value.part_id]){
                    answersByPart[value.part_id] = [];
                }
                answersByPart[value.part_id].push(value);
            });
            $scope.answers = answersByPart[part_id];
    });
    WebworkService.groupedPartAnswers(course, set_id, problem_id, part_id).success(function(data){
        console.log(data);
        $scope.grouped_answers = data;
    }).error(function(data){
        console.error(data);
    });

    $scope.scrollTo = function($event) {
        $event.preventDefault();
        var id = $($event.target).attr('href').substr(1);
        var old = $location.hash();
        $location.hash(id);
        $anchorScroll();
        //reset to old to keep any additional routing logic from kicking in
        $location.hash(old);
    };

    WebworkService.problemPGPath(course, set_id, problem_id).success(function(data){
        $scope.pg_path = JSON.parse(data);
    });

    WebworkService.problemPGFile(course, set_id, problem_id).success(function(data){
        $scope.pg_file = JSON.parse(data);
        var re = /\[__+\]{(?:Compute\(")(.+)(?:"\))}/g;
        var i = 1;
        var match;
        while(i < part_id){
            match = re.exec($scope.pg_file);
            i++;
        }
        if(match && match[1]){
            $scope.answer_expression = match[1];
        }
    });

    var sock = SockJSService.get_sock();
    sock.onmessage = function(event) {
        print("RECEIVED: " + event.data);
        var data = JSON.parse(event.data);
        if (data.type === "my_students"){
            //$scope.my_students = data.arguments;
        }else if (data.type === "unassigned_students"){
            $scope.unassigned_students = data.arguments.filter(function(student){
                return student.problem_id == problem_id;
            });
        }
    };

    $scope.sum = function(group){
        var s = 0;
        for (g in group){
            s = s + group[g].length;
        }
        return s;
    };

    $scope.match_hint_id = function(id){
        var i = 0;
        var data = $scope.hints;
        for (i=0; i<data.length; i++){
            if (data[i].hint_id == id){
                return data[i].pg_text;
            }
        }
        return "no matching hint";
    };

});
