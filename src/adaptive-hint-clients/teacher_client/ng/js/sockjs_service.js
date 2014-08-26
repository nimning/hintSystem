var App = angular.module('ta-console');

// Debug print
function print(msg) {
   // console.log(msg);
}
App.factory('SockJSService', function($http, $window, $rootScope, $location, $interval, APIHost) {
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
            print("SockJS not connected")
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
            console.log(this);
	        factory.send_command('teacher_join',
			                     { 'teacher_id' : teacher_id });
	    };

	    sock.onclose = function() {
	        print("INFO: disconnected");
            connected = false;
	    };

        return sock;

    };


    return factory;
});
