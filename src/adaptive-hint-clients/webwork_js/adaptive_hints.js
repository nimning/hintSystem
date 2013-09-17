(function() {

    // Send a command to SockJS server.
    function send_command(sock, cmd, args) {
	sock.send(JSON.stringify({"type": cmd,
				  "arguments": args}));
	console.log("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
    }

    // Send 'student_answer' message
    function student_answer(box) {
	if (box.value.length > 0) {
	    var args = { 'boxname': box.attributes["name"].value,
			 'value': box.value };

	    send_command(sock, 'student_answer', args);
	    box['last_answer'] = box.value;
	}
    }

    // Create actions for a textbox
    function create_textbox_actions(textbox) {
	// When a textbox loses focus
	textbox.blur(function() {
	    // invalidate existng timeout
	    if (this['timer']) {
		window.clearTimeout(this['timer']);
	    }

	    // Send 'student_answer' command if needed
	    if (!this['last_answer'] || this['last_answer'] != this.value) {
		student_answer(this);
	    } 
	});

	// When a keyup is detected
	textbox.keyup(function() {
	    // invalidate existing timeout
	    if (this['timer']) {
		window.clearTimeout(this['timer']);
	    }

	    // create a new timeout
	    this['timer'] = window.setTimeout(function(obj) {
		// when the timeout is reached, send answer
		if (!obj['last_answer'] || obj['last_answer'] != obj.value) {
		    student_answer(obj);
		}
	    }, 1500, this);
	});
    }
    
    function remove_all_hints() {
	$('div[id^=wrapper_]').remove()
    }

    // Insert a hint to a given location.
    function insert_hint(hint_html, location, hintbox_id) {
	var d = document.createElement('div');
	d.setAttribute('id', 'wrapper_' + hintbox_id);
	d.innerHTML = hint_html;
	$("input#" + location).before(d);
	var hintbox = $("input#"+hintbox_id);
	create_textbox_actions(hintbox);
    }

    // Update the color of an answer box based on answer status 
    function update_answerbox(box_id, is_correct, error_msg, entered_value) {
	var box = $("input#" + box_id);
	
	if (!box) return;

	// Set value if the box is empty
	if (box.val().length == 0) {
	    box.val(entered_value);
	}
	// Remove previous title
	box.attr('title', '');
	if (error_msg && error_msg.length > 0) {
	    box.attr('title', error_msg);
	    box.attr('style','background-color: #ffcc66;');
	} else {
	    if (is_correct) {
		box.attr('style','background-color: #55ff55;');
	    }
	    else {
		box.attr('style','background-color: #ff5555;');
	    }
	}
    }

    $(document).ready(function() {
	// Gather student's info
	var pathArray = window.location.pathname.split('/');
	var course_id = pathArray[2];
	var set_id = pathArray[3];
	var problem_id = pathArray[4];
	var student_id = $("input#hidden_effectiveUser").val();
	var session_id = $("input#hidden_key").val();

	// Create a SockJS connection to the server
	sock = new SockJS("http://webwork.cse.ucsd.edu:4350/student");

	sock.onopen = function() {
	    console.log("INFO: connected");
	    // Send `signin` command
	    var params = {
		'session_id': session_id,
		'student_id': student_id,
		'course_id' : course_id,
		'set_id': set_id,
		'problem_id': problem_id,
		'problem_body': $("div#problem-content").html(),
		'pg_file' : $("input[name=displayMode]").next().attr('value')
	    };
	    send_command(sock, 'student_join', params);
	};

	sock.onmessage = function(e) {
	    console.log("RECIEVED: " + e.data);
	    message = $.parseJSON(e.data);
    	    // Process the received messages here.
    	    // If...
    	    //   message = 'hint': insert the hint to a proper place.
    	    //                     Register actions with the new box.
	    if (message['type'] == 'hints') {
		hints = message['arguments'];
		remove_all_hints();
		for (var i=0; i < hints.length; i++) {
		    hint = hints[i];
		    insert_hint(hint['hint_html'],
				hint['location'],
				hint['hintbox_id']);
		}
	    }
    	    //   message = 'answer_status': set color of the box according the correctness.
    	    //    Correct = blue, Incorrect = red, Malformed answer = orange
	    else if (message['type'] == 'answer_status') {
		answer_statuses = message['arguments'];
		for (var i=0; i < answer_statuses.length; i++) {
		    answer_status = answer_statuses[i];
		    update_answerbox(answer_status['boxname'], 
				     answer_status['is_correct'], 
				     answer_status['error_msg'],
				     answer_status['entered_value']);
		}
	    }
	};

	sock.onclose = function() {
	    console.log("INFO: disconnected");
	};

	// Associates actions to answer boxes.
	var answer_boxes = $("input[id^=AnSwEr]");
	create_textbox_actions(answer_boxes);

	console.log("INFO: document loaded");
    });  

})();
