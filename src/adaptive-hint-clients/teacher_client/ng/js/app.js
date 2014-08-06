console.log("App!");
var App = angular.module('ta-console', ['ngRoute', 'ngSanitize', 'datatables']);

App.config(
    ['$routeProvider', '$httpProvider',
     function($routeProvider, $httpProvider) {

         $httpProvider.defaults.useXDomain = true;
         delete $httpProvider.defaults.headers.common['X-Requested-With'];
         $httpProvider.interceptors.push('authInterceptor');

         $routeProvider.
             when('/:course', {
                 templateUrl: 'partials/course.html',
                 controller: 'CourseCtrl'
             }).
             when('/:course/sets/:set_id', {
                 templateUrl: 'partials/set.html',
                 controller: 'SetCtrl'
             }).
             when('/:course/sets/:set_id/problems/:problem_id', {
                 templateUrl: 'partials/problem.html',
                 controller: 'ProblemCtrl'
             }).
             when('/:course/login', {
                 templateUrl: 'partials/login.html',
                 controller: 'LoginCtrl'
             }).
             when('/:course/console', {
                 templateUrl: 'partials/console.html',
                 controller: 'TAConsoleCtrl'
             }).
             otherwise({
                 redirectTo: '/'
             });
     }]);

App.constant('APIHost', 'webwork.cse.ucsd.edu');

App.value('CurrentCourse', {name: 'Course'});

App.controller('ApplicationCtrl', function($routeParams, CurrentCourse){

});
