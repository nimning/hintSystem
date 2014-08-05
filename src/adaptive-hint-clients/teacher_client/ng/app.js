// Code goes here

var App = angular.module('ta-console', ['ngRoute', 'ngSanitize']);

App.config(
    ['$routeProvider', '$httpProvider',
     function($routeProvider, $httpProvider) {

         $httpProvider.defaults.useXDomain = true;
         delete $httpProvider.defaults.headers.common['X-Requested-With'];
         $httpProvider.interceptors.push('authInterceptor');

         $routeProvider.
             when('/:course/login', {
                 templateUrl: 'partials/login.html',
                 controller: 'LoginCtrl'
             }).
             when('/analyze_problem', {
                 templateUrl: 'partials/analyze_problem.html',
                 controller: 'AnalyzeProblemCtrl'
             }).
             when('/:course/console', {
                 templateUrl: 'partials/console.html',
                 controller: 'TAConsoleCtrl'
             }).

             otherwise({
                 redirectTo: '/login'
             });
     }]);

