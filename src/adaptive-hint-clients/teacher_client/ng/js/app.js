var App = angular.module(
    'ta-console',
    ['ngRoute', 'ngSanitize', 'datatables', 'ta-console.directives',
     'smart-table', 'angularMoment', 'ui.codemirror', 'ui.ladda',
     'mgcrea.ngStrap', 'mgcrea.ngStrap.helpers.dimensions',
     'mgcrea.ngStrap.scrollspy', 'ui.router']);
var directives = angular.module('ta-console.directives', []);
App.config(
    ['$httpProvider', '$locationProvider', '$stateProvider',
     '$urlRouterProvider',
     function($httpProvider, $locationProvider, $stateProvider,
             $urlRouterProvider) {

         $httpProvider.defaults.useXDomain = true;
         delete $httpProvider.defaults.headers.common['X-Requested-With'];
         $httpProvider.interceptors.push('authInterceptor');
         $urlRouterProvider.otherwise('/');
         $stateProvider.
             state('course', {
                 url: '/:course',
                 templateUrl: 'partials/course.html',
                 controller: 'CourseCtrl',
                 title: '{{course}}',
                 loginRequired: true
             }).
             state('set', {
                 url: '/:course/sets/:set_id',
                 templateUrl: 'partials/set.html',
                 controller: 'SetCtrl',
                 title: '{{set_id}}',
                 loginRequired: true
             }).
             state('problem', {
                 url: '/:course/sets/:set_id/problems/:problem_id',
                 templateUrl: 'partials/problem.html',
                 controller: 'ProblemCtrl',
                 title: '{{set_id}} #{{problem_id}}',
                 loginRequired: true
             }).
             state('problem_user', {
                 url: '/:course/sets/:set_id/problems/:problem_id/users/:user_id',
                 templateUrl: 'partials/problem_user.html',
                 controller: 'ProblemUserCtrl',
                 title: '{{set_id}} #{{problem_id}} - {{user_id}}',
                 loginRequired: true
             }).
             state('login', {
                 url: '/:course/login',
                 templateUrl: 'partials/login.html',
                 controller: 'LoginCtrl',
                 title: 'Log In',
                 loginRequired: false
             }).
             state('home', {
                 url: '/',
                 templateUrl: 'partials/home.html',
                 controller: 'HomeCtrl',
                 title: 'Courses'
             });
     }])
    .run(function ($rootScope, $location, AUTH_EVENTS, AuthService, MessageService) {
        $rootScope.$on('$routeChangeStart', function (event, next) {
            MessageService.clear();
            if(next.loginRequired){
                if (!AuthService.isAuthenticated()) {
                    $rootScope.$broadcast(AUTH_EVENTS.notAuthenticated);
                    if(next.params.course){
                        $location.path('/'+next.params.course+'/login');
                        MessageService.addWarning('You must log in!');
                    } else{
                        $location.path('/');
                    }
                }
            }
        });
    });;

App.constant('APIHost', 'webwork.cse.ucsd.edu');

App.value('CurrentCourse', {name: 'Course'});

App.controller('ApplicationCtrl', function($scope, $stateParams, $route, $rootScope, $interpolate,
                                           SockJSService, CurrentCourse, Session, AUTH_EVENTS, MessageService){
    if(Session.user_id){
        var sock = SockJSService.connect(4350, Session.user_id);
    }

    $rootScope.$on("$stateChangeSuccess", function(currentRoute, previousRoute){
        if($stateParams.course){
            CurrentCourse.name = $stateParams.course;
        }
        //Change page title, based on Route information
        if(false){ //$route.current.title){
            var titleExp = $interpolate($route.current.title);
            $rootScope.title = titleExp($route.current.params);
        }else{
            $rootScope.title="";
        }
    });

    $rootScope.$on(AUTH_EVENTS.loginSuccess, function(event){
        if(Session.user_id){
            var sock = SockJSService.connect(4350, Session.user_id);
        }
    });

    $rootScope.$on(AUTH_EVENTS.logoutSuccess, function(event){
        SockJSService.disconnect();
    });

    $rootScope.$on('messages-updated', function(newVal, oldval){
        $scope.messages = MessageService.messages;
    });

});
