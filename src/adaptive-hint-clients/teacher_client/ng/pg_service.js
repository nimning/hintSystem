var App = angular.module('ta-console');

App.factory('PGService', function($http, $window, $rootScope, $location) {
    return {
        render: function(pg_file, seed, fn) {
            $http
                .post('http://192.168.33.10:4351/render',
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
