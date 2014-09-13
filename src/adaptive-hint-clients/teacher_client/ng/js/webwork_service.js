var App = angular.module('ta-console');

App.factory('WebworkService', function($http, $window, $rootScope, $location, $q, APIHost) {
    var factory = {
        sets: function(course, fn) {
            $http
                .get('http://'+APIHost+':4351/sets',
                     {params: {course: course}})
                .success(function (data, status, headers, config) {
                    fn(data);
                });
        },
        problems: function(course, set_id, fn) {
            return $http
                .get('http://'+APIHost+':4351/problems',
                     {params: {course: course, set_id: set_id}});
        },
        problemHints: function(course, set_id, problem_id) {
            return $http
                .get('http://'+APIHost+':4351/problem_hints',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        exportProblemData: function(course, set_id, problem_id) {
            return $http
                .get('http://'+APIHost+':4351/export_problem_data',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        problemPGFile: function(course, set_id, problem_id) {
            return $http
                .get('http://'+APIHost+':4351/pg_file',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        problemSeed: function(course, set_id, problem_id, user_id) {
            return $http
                .get('http://'+APIHost+':4351/problem_seed',
                     {params: {course: course, set_id: set_id,
                               problem_id: problem_id, user_id: user_id}});
        },
        answersByPart: function(course, set_id, problem_id, user_id) {
            return $http
                .get('http://'+APIHost+':4351/answers_by_part',
                     {params: {course: course, set_id: set_id, problem_id: problem_id,
                               user_id: user_id}});
        },

        render: function(pg_file, seed) {
            if(pg_file[0]!=='/'){ // Don't base64 encode absolute paths
                pg_file = btoa(unescape(encodeURIComponent(pg_file)));
            }
            return $http
                .post('http://'+APIHost+':4351/render',
                      {pg_file: pg_file, seed: seed.toString()});
        },
        previewHint: function(hint, seed, feedback){
            var deferred = $q.defer();
            factory.render(hint.pg_header+hint.pg_text+hint.pg_footer, seed).success(function (data){
	            var err = data.error_msg;
	            // Clean up
	            var clean_html = data.rendered_html.replace(/[\s\S]*?<div/m, '<div').trim();
	            // Rename answer box
	            var hint_id = hint.hint_id;
	            var assigned_hintbox_id = 'HINTBOXID';
	            clean_html = clean_html.replace(/AnSwEr0001/g, assigned_hintbox_id);
	            // Include feedback?
	            if (feedback) {
		            clean_html += '<div style="clear:left;">' +
		                '<input type="radio" name="feedback_' +
		                assigned_hintbox_id + '" value="too hard">Too hard' +
		                '<input type="radio" name="feedback_' +
		                assigned_hintbox_id + '" value="easy but unhelpful">Easy but unhelpful' +
		                '<input type="radio" name="feedback_' +
		                assigned_hintbox_id + '" value="helpful">Helpful' +
		                '</div>';
	            }
                deferred.resolve(clean_html);
            }).error(function(err){
                deferred.reject(err);
            });
            return deferred.promise;
        },
        createHint: function(course, set_id, problem_id, author, pg_text){
            return $http
                .post('http://'+APIHost+':4351/hint',
                      {course: course, set_id: set_id, problem_id: problem_id,
                       author: author, pg_text: pg_text.replace(/\\/g,"\\\\")});
        },
        updateHint: function(course, hint_id, pg_text){
            return $http
                .put('http://'+APIHost+':4351/hint',
                     {course: course, hint_id: hint_id, pg_text: pg_text.replace(/\\/g,"\\\\")});
        },
        deleteHint: function(course, hint_id){
            return $http
                .delete('http://'+APIHost+':4351/hint',
                        {params: {course: course, hint_id: hint_id}});
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
    return factory;
});
