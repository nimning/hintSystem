var App = angular.module('ta-console');

App.factory('WebworkService', function($http, $window, $rootScope, $location, APIHost) {
    return {
        sets: function(course, fn) {
            $http
                .get('http://'+APIHost+':4351/sets',
                     {params: {course: course}})
                .success(function (data, status, headers, config) {
                    fn(data);
                });
        },
        problems: function(course, set_id, fn) {
            $http
                .get('http://'+APIHost+':4351/problems',
                     {params: {course: course, set_id: set_id}})
                .success(function (data, status, headers, config) {
                    fn(data);
                });
        },
        exportProblemData: function(course, set_id, problem_id, fn) {
            $http
                .get('http://'+APIHost+':4351/export_problem_data',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}})
                .success(function (data, status, headers, config) {
                    fn(data);
                });
        },
        render: function(pg_file, seed, fn) {
            $http
                .post('http://'+APIHost+':4351/render',
                      {pg_file: btoa(pg_file), seed: seed})
                .success(function (data, status, headers, config) {
                    fn(data);
                })
                .error(function (data, status, headers, config) {

                });
        },
        logOut: function() {
        }
    };
});
