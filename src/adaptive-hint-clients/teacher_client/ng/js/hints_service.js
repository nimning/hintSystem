var App = angular.module('ta-console');

App.factory('HintsService', function($http, $window, $rootScope, $location, $q,
                                     APIHost, APIPort, WebworkService) {
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
                      {course: course, set_id: set_id, problem_id: problem_id, part_id: part_id,
                       author: author, pg_text: pg_text.replace(/\\/g,"\\\\")});
        },
        updateHint: function(course, hint_id, pg_text){
            return $http
                .put(BASE_URL+'/hint',
                     {course: course, hint_id: hint_id, pg_text: pg_text.replace(/\\/g,"\\\\")});
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
        assignedHintHistory: function(course, hint_id){
            return $http
                .get(BASE_URL+'/assigned_hint_history',
                     {params: {course: course, hint_id: hint_id}});
        }

    };
    return factory;
});
