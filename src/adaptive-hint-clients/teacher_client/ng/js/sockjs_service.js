var App = angular.module('ta-console');

// Debug print
function print(msg) {
   // console.log(msg);
}

App.constant('SOCKJS_EVENTS', {
    connected: 'sockjs-connected',
    disconnected: 'sockjs-disconnected',
    msgReceived: 'sockjs-message-received'
});

App.factory('SockJSService', function($http, $window, $rootScope, $location, $interval, $q,
                                      $timeout, APIHost, SOCKJS_EVENTS) {
    var factory = {};
    var sock;
    var connected = false;
    var user_id;
    var my_port;
    factory.connected = function(){
        return connected;
    };
    factory.send_command = function (cmd, args) {
        if(!connected){
            console.error("SockJS not connected");
            // if(user_id){ // Auto reconnect SockJS
            //     factory.connect(my_port, user_id);
            //     $timeout(function(){
            //         factory.send_command(cmd, args);
            //     }, 1000);

            // }
        }else{
            sock.send(JSON.stringify({
                "type" : cmd,
                "arguments" : args
            }));
            print("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
        }
    };

    factory.connect = function(port, teacher_id){
        print("Connecting websocket");
	    sock = new SockJS('http://' + APIHost + ':' +
			                  port +
			                  '/teacher');
        user_id = teacher_id;
        my_port = port;
	    sock.onopen = function() {
	        console.info("SockJS connected");
            connected = true;
	        factory.send_command('teacher_join',
			                     { 'teacher_id' : teacher_id });
            $rootScope.$emit(SOCKJS_EVENTS.connected);
	    };

	    sock.onclose = function() {
	        console.info("SockJS disconnected");
            connected = false;
	    };

        sock.onmessage = function(e){
            print("RECIEVED: " + e.data);
	        var data = JSON.parse(e.data);
            $rootScope.$emit(SOCKJS_EVENTS.msgReceived, data);
        };

        return sock;

    };

    factory.disconnect = function(){
        if(connected){
            sock.close();
        }
    };
    factory.teacher_join = function(teacher_id, course_id, set_id, problem_id, student_id){
        factory.send_command('teacher_join', {
            teacher_id: teacher_id, course_id: course_id, set_id: set_id,
            problem_id: problem_id, student_id: student_id
        });
    };

    factory.request_student = function(course_id, set_id, problem_id, student_id){
        factory.send_command('request_student', {
            course_id: course_id, set_id: set_id, problem_id: problem_id,
            student_id: student_id
        });
    };

    factory.release_student = function(course_id, set_id, problem_id, student_id){
        factory.send_command('release_student', {
            course_id: course_id, set_id: set_id, problem_id: problem_id,
            student_id: student_id
        });
    };

    factory.get_student_info = function(course_id, set_id, problem_id, student_id){
        factory.send_command('get_student_info', {
            course_id: course_id, set_id: set_id, problem_id: problem_id,
            student_id: student_id
        });
    };

    factory.add_hint = function(course_id, set_id, problem_id, student_id, location, hint_id, hint_html_template){
        factory.send_command('add_hint', {
            student_id: student_id, course_id: course_id, set_id: set_id,
            problem_id: problem_id, location: location, hint_id: hint_id,
            hint_html_template: hint_html_template
        });
    };

    factory.onConnect = function(){
        var deferred = $q.defer();
        if(connected){
            deferred.resolve();
        }else{
            $rootScope.$on(SOCKJS_EVENTS.connected, function(){
                deferred.resolve();
            });
        }
        return deferred.promise;
    };

    factory.onMessage = function(fn){
        console.log("Attaching event handler");
        var handler = $rootScope.$on(SOCKJS_EVENTS.msgReceived, fn);
        $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
            // Deregister event handler when changing pages
            console.info('Destroying event handler');
            handler();
        });
    };
    return factory;
});
