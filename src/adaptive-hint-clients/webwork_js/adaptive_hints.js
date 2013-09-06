(function() {


// Send a command to SockJS server
function send_command(sock, cmd, args) {
    sock.send(JSON.stringify({"type": cmd,
			      "arguments": args}));
    console.log("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
}


$(document).ready(function() {
    
    // Gather student's info
    var pathArray = window.location.pathname.split('/');
    var course_id = pathArray[2];
    var set_id = pathArray[3];
    var problem_id = pathArray[4];
    var student_id = $("#hidden_effectiveUser").val();

    // Create a SockJS connection to the server
    sock = new SockJS("http://webwork.cse.ucsd.edu:4350/student");

    sock.onopen = function() {
	console.log("INFO: connected");
	// Send `signin` command
	var params = {
	    'student_id': student_id,
	    'course_id' : course_id,
	    'set_id': set_id,
	    'problem_id': problem_id,
	    'problem_body': $("#problem-content").html()
	};
	send_command(sock, 'signin', params);
    };

    sock.onmessage = function(e) {
    	// Process the received messages here.
    	// If...
    	//   message = 'hint': insert the hint to a proper place.
    	//                     Register actions with the new box.
    	//   message = 'answer_status': set color of the box according the correctness.
    	//    Correct = blue, Incorrect = red, Malformed answer = orange
	console.log("RECIEVED: " + e.data);
    };

    sock.onclose = function() {
	console.log("INFO: disconnected");
    };
	
    // When a textbox loses focus, send the updated value to server.
    $("[id^=AnSwEr]").blur(function() {
	// Send 'newstring' command
	var args = { 'boxname': this.attributes["name"].value,
		     'value': this.value };
	send_command(sock, 'newstring', args);
    });

    // Add a handler for time-out on "[id^=AnSwEr]"

    console.log("INFO: document loaded");
});  

})();
