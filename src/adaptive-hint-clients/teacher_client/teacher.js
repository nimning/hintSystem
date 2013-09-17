// require jQuery

function print(msg) {
    var textbox = $("#textarea");
    textbox.val(textbox.val() + msg + "\n");
    textbox.scrollTop(
        textbox[0].scrollHeight - textbox.height()
    );
}

// Send a command to SockJS server
function send_command(sock, cmd, args) {
    sock.send(JSON.stringify({"type": cmd,
			      "arguments": args}));
    print("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
}

$(document).ready(function() {
    sock = new SockJS('http://webwork.cse.ucsd.edu:4349/teacher');
    sock.onopen = function() {
	print("INFO: connected");
	var randomNum = Math.ceil(Math.random()*10000);
	teacher_id = 'teacher' + randomNum;
	send_command(sock, 
		     'teacher_join', 
		     {'teacher_id': teacher_id});
    };
    sock.onmessage = function(e) {
	print("RECIEVED: " + e.data);
    };
    sock.onclose = function() {
	print("INFO: disconnected");
    };
	
    $("#list_students").click(function() {
	send_command(sock, 'list_students', {});
    });

    $("#add_hint").click(function() {
	send_command(sock, 'add_hint', {
	    'session_id': $('#hint_session_id').val(),
	    'course_id': $('#hint_course_id').val(),
	    'set_id': $('#hint_set_id').val(),
	    'problem_id': $('#hint_problem_id').val(),
	    'location': $('#hint_location').val(),
	    'hintbox_id': $('#hintbox_id').val(),
	    'hint_html': $('#hint_html').val()
	});
    });
	
    print("INFO: document loaded");
	
});  
