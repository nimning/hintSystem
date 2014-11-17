var App = angular.module('ta-console');

App.factory('HintsService', function($http, $window, $rootScope, $location, $q, $timeout,
                                     APIHost, APIPort, WebworkService, SockJSService) {
    var BASE_URL = 'http://'+APIHost+':'+APIPort;
    var factory = {
        previewHint: function(hint, seed, feedback){
            // TODO Need to use PSVN here as well
            var deferred = $q.defer();
            WebworkService.render(hint.pg_header+'\n'+hint.pg_text+'\n'+hint.pg_footer, seed).success(function (data){
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
        createHint: function(course, set_id, problem_id, part_id, author, pg_text){
            return $http
                .post(BASE_URL+'/hint',
                      {course: course, set_id: set_id, problem_id: problem_id, part_id: parseInt(part_id),
                       author: author, pg_text: pg_text.replace(/\\/g,"\\\\")});
        },
        updateHint: function(course, hint_id, pg_text, part_id){
            return $http
                .put(BASE_URL+'/hint',
                     {course: course, hint_id: hint_id, pg_text: pg_text.replace(/\\/g,"\\\\"),
                      part_id: part_id});
        },
        deleteHint: function(course, hint_id){
            return $http
                .delete(BASE_URL+'/hint',
                        {params: {course: course, hint_id: hint_id}});
        },
        hintFilters: function(course) {
            return $http
                .get(BASE_URL+'/hint_filter',
                     {params: {course: course}});
        },
        getHintFilter: function(course, hint_id) {
            return $http
                .get(BASE_URL+'/assigned_hint_filter',
                     {params: {course: course, hint_id: hint_id}});
        },
        createHintFilter: function(course, hint_id, filter_id, trigger_cond){
            return $http
                .post(BASE_URL+'/assigned_hint_filter',
                     {course: course, hint_id: hint_id,
                               hint_filter_id: filter_id, trigger_cond: trigger_cond});
        },
        updateHintFilter: function(course, hint_id, filter_id, trigger_cond){
            return $http
                .put(BASE_URL+'/assigned_hint_filter',
                     {course: course, hint_id: hint_id,
                               hint_filter_id: filter_id, trigger_cond: trigger_cond});
        },
        assignedHintHistoryByHintID: function(course, hint_id){
            return $http
                .get('http://'+APIHost+':4351/assigned_hint_history_by_hint_id',
                     {params: {course: course, hint_id: hint_id}});
        },
        assignedHintHistoryByProblemPart: function(course, problem_id, set_id, pg_id){
            return $http
                .get('http://'+APIHost+':4351/assigned_hint_history_by_problem_part',
                     {params: {course: course, problem_id: problem_id, set_id:set_id, pg_id: pg_id}});
        },
        assignedHintHistoryOfProblem: function(course, set_id, problem_id){
            return $http
                .get('http://'+APIHost+':4351/assigned_hint_history_of_problem',
                     {params: {course: course, set_id: set_id, problem_id: problem_id}});
        },
        createFilterFunction: function(name, course, author, code, set_id, problem_id){
            return $http
                .post(BASE_URL+'/filter_functions',
                      {name: name, course: course, author: author, code: code, set_id: set_id,
                       problem_id: problem_id});
        },
        updateFilterFunction: function(id, code){
            return $http
                .put(BASE_URL+'/filter_functions',
                     {id: String(id), code: code});
        },

        getFilterFunctions: function(args){
            return $http
                .get(BASE_URL+'/filter_functions',
                     {params: args});
        },
        sendHintToUsers: function(students, hint, course, part_id){
            // Send a hint to multiple users
            var set_id = hint.set_id;
            var problem_id = hint.problem_id;
            for (var i=0; i <students.length; i++){
                var hint_html_template = "";
                $timeout(function(student){ // Render with a random delay.
                    // TODO Flatten promise chain
                    WebworkService.problemSeed(course, set_id, problem_id, student).success(function(seed){
                        factory.previewHint(hint, seed, true).
                            then(function(rendered_html){
                                console.log(rendered_html);
                                hint_html_template = rendered_html;
                                SockJSService.add_hint(course, set_id, problem_id, student,
                                                       "AnSwEr"+("0000"+part_id).slice(-4), hint.hint_id, hint_html_template);
                            }, function(error){
                                console.error(error);
                            });

                    });
                    // the callback might execute after the end of the loop so we need to bind the value of student inside the loop
                }.bind(this, students[i]), 2000*Math.random());
            }

        }
    };
    return factory;
});
