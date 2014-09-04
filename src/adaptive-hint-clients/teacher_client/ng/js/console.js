var App = angular.module('ta-console');

App.controller('TAConsoleCtrl', function ($scope, $http) {
    $scope.assignments = [
        {
            name: "Assignment1",
            students: 0,
            due: "2014-08-01T18:00:00Z"
        },
        {
            name: "Assignment2",
            students: 2,
            due: "2014-08-02T18:00:00Z"
        },
        {
            name: "Assignment3",
            students: 36,
            due: "2014-08-05T18:00:00Z"
        },
        {
            name: "Assignment4",
            students: 11,
            due: "2014-08-07T18:00:00Z"
        },
        {
            name: "Assignment5",
            students: 0,
            due: "2014-08-12T18:00:00Z"
        },
        {
            name: "Assignment6",
            students: 0,
            due: "2014-08-13T18:00:00Z"
        },
        {
            name: "Assignment7",
            students: 0,
            due: "2014-08-14T18:00:00Z"
        },
        {
            name: "Assignment8",
            students: 0,
            due: "2014-08-15T18:00:00Z"
        },

    ];
    
    problems = {
        Assignment3: [
            {
                number: 1,
                students: 3
            },
            {
                number: 2,
                students: 5
            },
            {
                number: 3,
                students: 20
            },
            {
                number: 4,
                students: 8
            }
        ],
        Assignment2: [
            {
                number: 1,
                students: 0
            },
            {
                number: 2,
                students: 0
            },
            {
                number: 3,
                students: 1
            },
            {
                number: 4,
                students: 1
            }
        ],
        Assignment4: [
            {
                number: 1,
                students: 3
            },
            {
                number: 2,
                students: 4
            },
            {
                number: 3,
                students: 3
            },
            {
                number: 4,
                students: 1
            }
        ],
    };
    $scope.orderKey = "students";
    $scope.reverse = true;
    $scope.assignmentFilter = function(assignment){
        if ($scope.assignmentsWoStudents){
            return true;
        }else{
            return assignment.students > 0;
        }
    };

    $scope.problems = [];
    $scope.showAssignment = function(assignment){
        $scope.currentAssignment = assignment;
        $scope.problems = problems[assignment.name];
        console.log($scope.currentAssignment.name == assignment.name);
        $scope.currentProblem = {};
    };

    $scope.showProblem = function(problem){
        $scope.currentProblem = problem;
    };

    $http.post('http://192.168.33.10:4351/render', {pg_file: "foo.pg", seed: "1"})
        .success(function (data, status, headers, config){
            console.log("hi");
            console.log(data);
            console.log(headers);
        })
        .error(function (data, status, headers, config){
            console.log("darn");
            console.log(data);
            console.log(config);
        });

});
