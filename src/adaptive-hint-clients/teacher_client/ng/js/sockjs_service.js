var App = angular.module('ta-console');

// Debug print
function print(msg) {
   // console.log(msg);
}
App.factory('SockJSService', function($http, $window, $rootScope, $location, $interval, $timeout, APIHost) {
    var factory = {};
    var sock;
    var connected = false;
    factory.connected = function(){
        return connected;
    };
    factory.get_sock = function() {
        return sock;
    };
    factory.send_command = function (cmd, args) {
        if(!connected){
            print("SockJS not connected");
            $timeout(function(){
                factory.send_command(cmd, args);
            }, 100);
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

	    sock.onopen = function() {
	        print("INFO: connected");
            connected = true;
	        factory.send_command('teacher_join',
			                     { 'teacher_id' : teacher_id });
	    };

	    sock.onclose = function() {
	        print("INFO: disconnected");
            connected = false;
	    };

        return sock;

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
    return factory;
});
