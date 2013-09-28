(function() {

    // Debug print
    function print(msg) {
	console.log(msg);
    }

    // Send a message to SockJS server.
    function send_command(sock, msg, args) {
	sock.send(JSON.stringify({"type": msg,
				  "arguments": args}));
	print("SENT: " + msg + ":" + JSON.stringify(args, null, 2));
    }

    // Send 'student_answer' message.
    function student_answer(box) {
	if (box.value != box.last_answer) {
	    var args = { 'boxname': box.attributes["name"].value,
			 'value': box.value };
	    send_command(sock, 'student_answer', args);
	    box.last_answer = box.value;
	}
    }

    // Send 'hint_feedback' message.
    function hint_feedback(hintbox_id, feedback) {
	var args = { 'hintbox_id': hintbox_id,
		     'feedback': feedback };
	send_command(sock, 'hint_feedback', args);
    }

    // Create actions for a textbox.
    function create_textbox_actions(textbox) {
	
	// Initialize last answer to empty string.
	textbox.each(function() {
	    this.last_answer = '';	    
	});

	// When a textbox loses focus
	textbox.blur(function() {
	    student_answer(this);
	});

	// Also send answer if the enter key is detected.
	textbox.keydown(function(e) {
	    if (e.which == 13) {
		student_answer(this);
	    }
	});

	// Add Math button
	if (typeof textbox.addMathEditorButton == 'function') {
	    textbox.addMathEditorButton("PGML");
	}
    }
    
    function create_feedback_actions(hintbox_id) {
	$('input[name=feedback_' + hintbox_id + ']').change(function() {
	    hint_feedback(hintbox_id, $(this).val());
	});
    }

    // Remove all displayed hints. 
    function remove_all_hints() {
	$('div[id^=wrapper_]').remove();
    }

    // Insert a hint to a given location.
    function insert_hint(hint_html, location, hintbox_id) {
	var d = document.createElement('div');
	d.setAttribute('id', 'wrapper_' + hintbox_id);
	d.innerHTML = hint_html;
	d.setAttribute('style',
		       'background-color: #E0FAC0; ' +
		       'clear:left; ' +
		       'margin:10px; ' +
		       'border:1px solid; ' +
		       'padding:5px; ');
	$("input#" + location).before(d);
	var hintbox = $("input#"+hintbox_id);
	create_textbox_actions(hintbox);
	create_feedback_actions(hintbox_id);
    }

    // Update the color of an answer box based on answer status 
    function update_answerbox(box_id, is_correct, error_msg, entered_value) {
	var box = $("input#" + box_id);
	
	if (!box) return;

	// Set value if the box is empty
	if (box.val().length === 0) {
	    box.val(entered_value);
	}
	// Remove previous title
	box.attr('title', '');
	if (error_msg && error_msg.length > 0) {
	    box.attr('title', error_msg);
	    box.css('background-color', '#ffcc66');
	} else {
	    if (is_correct) {
		box.css('background-color', '#55ff55');
	    }
	    else {
		box.css('background-color', '#ff5555');
	    }
	}
    }

    ///////////////////////////////////////////////////////////////////
    
    $(document).ready(function() {

	// Gather student's info
	var pathArray = window.location.pathname.split('/');
	var course_id = pathArray[2];
	var set_id = pathArray[3];
	var problem_id = pathArray[4];
	var student_id = $("input#hidden_effectiveUser").val();
	var session_id = $("input#hidden_key").val();

	// SockJS server for each course 
	// Only courses listed here will be affected by this script.
	var router = {
	    'demo': 'http://webwork.cse.ucsd.edu:4350/student',
	    'CompoundProblems': 'http://webwork.cse.ucsd.edu:4349/student'
	};

	// Create a SockJS connection to the server
	if (router[course_id]) {
	    sock = new SockJS(router[course_id]);
	    
	    sock.onopen = function() {
		print("INFO: connected");
		// Send `student_join` message
		var params = {
		    'session_id': session_id,
		    'student_id': student_id,
		    'course_id' : course_id,
		    'set_id': set_id,
		    'problem_id': problem_id
		};
		send_command(sock, 'student_join', params);
	    };

	    sock.onmessage = function(e) {
		print("RECEIVED: " + e.data);
		var message = $.parseJSON(e.data);

		// Handle 'hints' message
		//  - Remove all displayed hints
		//  - Display the newly recieved hints
		if (message['type'] == 'hints') {
		    var hints = message['arguments'];
		    remove_all_hints();
		    for (var i=0; i < hints.length; i++) {
			var hint = hints[i];
			insert_hint(hint['hint_html'],
				    hint['location'],
				    hint['hintbox_id']);
		    }
		}

		// Handle 'answer_status' message
    		//  - Set color of the box according the correctness.
    		//     * Correct = blue 
		//     * Incorrect = red 
                //     * Malformed answer = orange
		else if (message['type'] == 'answer_status') {
		    var answer_statuses = message['arguments'];
		    for (var i=0; i < answer_statuses.length; i++) {
			var answer_status = answer_statuses[i];
			update_answerbox(answer_status['boxname'], 
					 answer_status['is_correct'], 
					 answer_status['error_msg'],
					 answer_status['entered_value']);
		    }
		}
	    };

	    sock.onclose = function() {
		print("INFO: disconnected");
	    };

	    // Associates actions to answer boxes.
	    var answer_boxes = $("input[id^=AnSwEr]");
	    create_textbox_actions(answer_boxes);
	}
	
	print("INFO: document loaded");
    });  

})();
