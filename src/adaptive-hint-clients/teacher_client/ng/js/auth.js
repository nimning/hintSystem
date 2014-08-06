var App = angular.module('ta-console');

App.controller('LoginCtrl', function($scope, $location, $window, $routeParams, AuthService){
    course = $routeParams.course;
    $scope.submit = function(){
        AuthService.logIn(course, $scope.username, $scope.password);
    };
}
);

App.factory('AuthService', function($http, $window, $rootScope, $location, APIHost) {
    return {
        logIn: function(course, username, password) {
            $http
                .post('http://'+APIHost+':4351/login',
                      {course: course, username: username, password: password})
                .success(function (data, status, headers, config) {
                    $window.sessionStorage.token = data.token;
                    var user = angular.fromJson($window.atob(data.token.split('.')[1]));

                    $window.sessionStorage.userId = user.user_id;
                    $rootScope.$emit("LoginController.login");
                    $location.path('/console');
                })
                .error(function (data, status, headers, config) {
                    // Erase the token if the user fails to login
                    delete $window.sessionStorage.token;
                    $rootScope.message = 'Error: Invalid email or password';
                });
        },
        logOut: function() {
        }
    };
});


App.factory('authInterceptor', function ($rootScope, $q, $window, $location) {
    return {
        request: function (config) {
            config.headers = config.headers || {};
            if($window.sessionStorage.token) {
                config.headers.Authorization = 'Bearer ' + $window.sessionStorage.token;
            }
            return config;
        },
        responseError: function (response) {
            if(response.status === 401) {
                $location.path('/login');
            }
            return $q.reject(response);
        }
    };
});
