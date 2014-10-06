var App = angular.module('ta-console');

App.controller('ProblemPartCtrl', function($scope, $location, $window, $stateParams,
                                           $sce, $timeout, $interval, $anchorScroll,
                                           WebworkService, SockJSService, APIHost){
    var course = $scope.course = $stateParams.course;
    var set_id = $scope.set_id = $stateParams.set_id;
    var problem_id = $scope.problem_id = $stateParams.problem_id;
    var part_id = $scope.part_id = $stateParams.part_id;

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
});
