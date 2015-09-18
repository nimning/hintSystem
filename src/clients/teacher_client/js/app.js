var App = angular.module(
    'ta-console',
    ['ngRoute', 'ngSanitize', 'datatables', 'ta-console.directives',
     'smart-table', 'angularMoment', 'ui.codemirror', 'ui.bootstrap',
     'mgcrea.ngStrap', 'mgcrea.ngStrap.helpers.dimensions',
     'mgcrea.ngStrap.scrollspy', 'ui.router', 'ui.bootstrap.typeahead']);

var directives = angular.module('ta-console.directives', []);

App.config(
    ['$httpProvider', '$locationProvider', '$stateProvider',
     '$urlRouterProvider',
     function($httpProvider, $locationProvider, $stateProvider,
             $urlRouterProvider) {

         $httpProvider.defaults.useXDomain = true;
         delete $httpProvider.defaults.headers.common['X-Requested-With'];
         $httpProvider.interceptors.push('authInterceptor');
         $urlRouterProvider.otherwise('/courses/CSE103_Fall14');
         $stateProvider.
            /*Parts and Courses were here in the same landing page.  Now only parts is shown in the landing page*/
             /*state('course', {
                 url: '/courses/:course',
                 templateUrl: 'partials/course.html',
                 controller: 'CourseCtrl',
                 title: '{{course}}',
                 loginRequired: true
             }).*/
             state('courses', {
                 url: '/courses/:course',
                 templateUrl: 'partials/parts.html',
                 controller: 'PartsCtrl',
                 title: '{{course}} Problem Parts',
                 loginRequired: true
             }).
             state('set', {
                 url: '/courses/:course/sets/:set_id',
                 templateUrl: 'partials/set.html',
                 controller: 'SetCtrl',
                 title: '{{set_id}}',
                 loginRequired: true
             }).
             state('problem', {
                 url: '/courses/:course/sets/:set_id/problems/:problem_id',
                 templateUrl: 'partials/problem.html',
                 controller: 'ProblemCtrl',
                 title: '{{set_id}} #{{problem_id}}',
                 loginRequired: true
             }).
             state('problem_user', {
                 url: '/courses/:course/sets/:set_id/problems/:problem_id/users/:user_id',
                 templateUrl: 'partials/problem_user.html',
                 controller: 'ProblemUserCtrl',
                 title: '{{set_id}} #{{problem_id}} - {{user_id}}',
                 loginRequired: true
             }).
             state('problem_part', {
                 url: '/courses/:course/sets/:set_id/problems/:problem_id/parts/:part_id',
                 templateUrl: 'partials/problem_part.html',
                 controller: 'ProblemPartCtrl',
                 title: '{{set_id}} #{{problem_id}} Part {{part_id}}',
                 loginRequired: true
             }).
             state('login', {
                 url: '/courses/:course/login',
                 templateUrl: 'partials/login.html',
                 controller: 'LoginCtrl',
                 title: 'Log In',
                 loginRequired: false
             }).
             state('home', {
                 url: '/courses',
                 templateUrl: 'partials/home.html',
                 controller: 'HomeCtrl',
                 title: 'Courses'
             });
     }])
    .run(function ($rootScope, $location, AUTH_EVENTS, AuthService, MessageService) {
        $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
            MessageService.clear();
            if(toState.loginRequired){
                if (!AuthService.isAuthenticated()) {
                    $rootScope.$broadcast(AUTH_EVENTS.notAuthenticated);
                    if(toParams.course){
                        $location.path('/courses/'+toParams.course+'/login');
                        MessageService.addWarning('You must log in!');
                    } else{
                        $location.path('/');
                    }
                }
            }
        });
    });;

App.controller('ApplicationCtrl', function($scope, $stateParams, $route, $rootScope, $interpolate,
                                           SockJSService, CurrentCourse, Session, AUTH_EVENTS, MessageService){
    if(Session.user_id){
        var sock = SockJSService.connect(4350, Session.user_id);
    }

    $rootScope.$on("$stateChangeSuccess", function(event, toState, toParams, fromState, fromParams){
        if($stateParams.course){
            CurrentCourse.name = $stateParams.course;
        }
        //Change page title, based on Route information
        if(toState.title){
            var titleExp = $interpolate(toState.title);
            $rootScope.title = titleExp($stateParams);
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
