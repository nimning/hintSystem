var SOCKJS_SERVER = 'http://webwork.cse.ucsd.edu';
var REST_SERVER = 'http://webwork.cse.ucsd.edu';

// Get the query string params
var QueryString = function() {
    // This function is anonymous, is executed immediately and
    // the return value is assigned to QueryString!
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
	var pair = vars[i].split("=");
	// If first entry with this name
	if (typeof query_string[pair[0]] === "undefined") {
            query_string[pair[0]] = pair[1];
            // If second entry with this name
	} else if (typeof query_string[pair[0]] === "string") {
            var arr = [query_string[pair[0]], pair[1]];
            query_string[pair[0]] = arr;
            // If third or later entry with this name
	} else {
            query_string[pair[0]].push(pair[1]);
	}
    }
    return query_string;
}();

// Debug print
function print(msg) {
  console.log(msg);
}

// Helper for sending a command to sockJS server
function send_command(sock, cmd, args) {
  sock.send(JSON.stringify({
    "type" : cmd,
    "arguments" : args
  }));
  print("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
}

// Helper for translating seconds to string
function secondsToString(seconds) {
    var numdays = Math.floor(seconds / 86400); 
    var numhours = Math.floor((seconds % 86400) / 3600);
    var numminutes = Math.floor(((seconds % 86400) % 3600) / 60);
    var ret = '<span title="' + seconds + '"></span>' + numminutes + "m";
    if (numhours > 0 || numdays > 0) {
	ret = numhours + "h " + ret;
    }
    if (numdays > 0) {
	ret = numdays + "d " + ret;
    }
    return ret;
}
