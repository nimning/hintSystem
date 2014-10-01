var App = angular.module('ta-console');

App.factory('HintsService', function($http, $window, $rootScope, $location, $q, APIHost) {
    var factory = {
        getHintFilter: function(course, hint_id) {
            return $http
                .get('http://'+APIHost+':4351/assigned_hint_filter',
                     {params: {course: course, hint_id: hint_id}});
        },
        createHintFilter: function(course, hint_id, filter_id, trigger_cond){
            return $http
                .post('http://'+APIHost+':4351/assigned_hint_filter',
                     {course: course, hint_id: hint_id,
                               hint_filter_id: filter_id, trigger_cond: trigger_cond});
        },
        updateHintFilter: function(course, hint_id, filter_id, trigger_cond){
            return $http
                .put('http://'+APIHost+':4351/assigned_hint_filter',
                     {course: course, hint_id: hint_id,
                               hint_filter_id: filter_id, trigger_cond: trigger_cond});
        }

    };
    return factory;
});
