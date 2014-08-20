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
            return $http
                .get('http://'+APIHost+':4351/export_problem_data',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        render: function(pg_file, seed, fn) {
            return $http
                .post('http://'+APIHost+':4351/render',
                      {pg_file: btoa(pg_file), seed: seed});
        },
        extractHeaderFooter: function(pg_text) {
            var re_header = /^[\s]*(TEXT\(PGML|BEGIN_PGML)[\s]+/gm;
	        var re_footer = /^[\s]*END_PGML[\s]+/gm;
	        var pg_header = re_header.exec(pg_text);
	        var pg_footer = re_footer.exec(pg_text);
	        if (pg_header && pg_footer) {
	            // reconstruct the footer
	            pg_header = pg_text.substr(0, pg_header.index) + '\nBEGIN_PGML\n';
	            pg_footer = pg_text.substr(pg_footer.index);
	            // Remove Solution section
	            pg_footer = pg_footer.replace(/^(BEGIN_PGML_SOLUTION|BEGIN_PGML_HINT)[\s\S]*END_PGML_SOLUTION/m,'');
	        }
            return {
                pg_header: pg_header,
                pg_footer: pg_footer
            };

        }
    };
});
