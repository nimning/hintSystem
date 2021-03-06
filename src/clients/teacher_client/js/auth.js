var App = angular.module('ta-console');

App.controller('LoginCtrl', function($scope, $location, $window, $stateParams, AuthService){
    var course = $scope.course = $stateParams.course;
    
    $scope.submit = function(){
        AuthService.logIn(course, $scope.username, $scope.password);
    };
});


App.constant('AUTH_EVENTS', {
  loginSuccess: 'auth-login-success',
  loginFailed: 'auth-login-failed',
  logoutSuccess: 'auth-logout-success',
  sessionTimeout: 'auth-session-timeout',
  notAuthenticated: 'auth-not-authenticated',
  notAuthorized: 'auth-not-authorized'
});

App.factory('AuthService', function($http, $window, $rootScope, $location,
                                    APIHost, APIPort, CurrentCourse, Session, AUTH_EVENTS, MessageService) {
    var BASE_URL = 'http://'+APIHost+':'+APIPort;
    return {
        logIn: function(course, username, password) {
            MessageService.clear();
            $http
                .post(BASE_URL+'/login',
                      {course: course, username: username, password: password})
                .success(function (data, status, headers, config) {
                    CurrentCourse.name = course;
                    Session.create(course, data.token);
                    $rootScope.$emit(AUTH_EVENTS.loginSuccess);
                    $location.path('/'+course);
                    MessageService.addInfo('Logged in!');
                })
                .error(function (data, status, headers, config) {
                    // Erase the token if the user fails to login
                    Session.destroy();
                    $rootScope.$emit(AUTH_EVENTS.loginFailed);
                    $rootScope.message = 'Error: Invalid email or password';
                    MessageService.addError('Login failed!');
                });
        },
        logOut: function() {
            Session.destroy();
            $rootScope.$emit(AUTH_EVENTS.logoutSuccess);
            $location.path('/');
            MessageService.addInfo('Logged out!');
        },
        isAuthenticated: function(){
            return Session.logged_in();
        }
    };
});

App.service('Session', function ($window) {
    this.create = function (course, token) {
        var user = angular.fromJson($window.atob(token.split('.')[1]));
        this.token = token;
        this.user_id = user.user_id;
        this.course = course;
        $window.localStorage.token = token;
        $window.localStorage.user_id = user.user_id;
        $window.localStorage.course = course;
    };
    this.destroy = function () {
        this.token = null;
        this.user_id = null;
        this.course = null;
        delete $window.localStorage.token;
        delete $window.localStorage.user_id;
    };

    this.logged_in = function(){
        return !!this.token;
    };
    if($window.localStorage.course && $window.localStorage.token){
        this.create($window.localStorage.course, $window.localStorage.token);
    }
    return this;
});

App.factory('authInterceptor', function ($rootScope, $q, $window, $location) {
    return {
        request: function (config) {
            config.headers = config.headers || {};
            if($window.localStorage.token) {
                config.headers.Authorization = 'Bearer ' + $window.localStorage.token;
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
