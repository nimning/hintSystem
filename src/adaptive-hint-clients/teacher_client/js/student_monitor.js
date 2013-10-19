// Pad 0's to a number
function pad(num, size) {
    var s = num + "";
    while (s.length < size) s = "0" + s;
    return s;
}

// Remove a hint from the student's view
function remove_hint(hintbox_id, location) {
    send_command(sock, 'remove_hint', {
	'student_id': $('#student_id').val(),
	'course_id': $('#course_id').val(),
	'set_id': $('#set_id').val(),
	'problem_id': $('#problem_id').val(),
	'location': location,
	'hintbox_id': hintbox_id
    });
}

// Render hint for preview
function render_hint(idx) {
    var pg_text = (hints[idx].pg_header + '\n' +
		   hints[idx].pg_text + '\n' +
		   hints[idx].pg_footer);
    var post_data = {
	'pg_file': btoa(pg_text),
	'seed': $('#pg_seed').val()
    };
    $('#hint_status').html('Rendering...');
    $.post(REST_SERVER + ':' + 
	   $('#rest_port').val() + '/render',
	   post_data, function(r) {
	       var err = r.error_msg;
	       // Clean up
	       var clean_html = r.rendered_html.replace(/[\s\S]*?<div/m, '<div').trim();
	       // Rename answer box
	       hint_id = hints[idx].hint_id;
	       assigned_hintbox_id = 'HINTBOXID'
	       clean_html = clean_html.replace(/AnSwEr0001/g, assigned_hintbox_id);
	       // Include feedback?
	       if ($('#feedback').is(':checked')) {
		   clean_html += '<div style="clear:left;">' +
		       '<input type="radio" name="feedback_' +
		       assigned_hintbox_id + '" value="too hard">Too hard' +
		       '<input type="radio" name="feedback_' +
		       assigned_hintbox_id + '" value="easy but unhelpful">Easy but unhelpful' +
		       '<input type="radio" name="feedback_' +
		       assigned_hintbox_id + '" value="helpful">Helpful' +
		       '</div>';
	       }
	       $('#hint_status').html('Preview');
	       $('#hint_html')
		   .html(clean_html)
		   .addClass('hint_html')
		   .show();
	       // Scroll to buttom of the page
	       window.scrollTo(0, document.body.scrollHeight);
	   });
}

function delete_hint(idx) {
    // Check ownership
    if (hints[idx].author != $('#teacher_id').val()) {
	alert("You can only delete hints that you created.");
	return;
    }
    // Confirmation
    var result = confirm("Delete hint_id=" + hints[idx].hint_id + "?");
    if (result == true) {
	$.ajax({
	    type: 'DELETE',
	    url: (REST_SERVER + ':' + $('#rest_port').val() + 
		  '/hint?course=' + $('#course_id').val() +
		  '&hint_id=' + hints[idx].hint_id),
	    success: function() {
		get_hints();
	    }
	});
    }
}


function fork_hint(idx) {
    var url = 'hint_editor.html';
    url += '?course_id=' + $('#course_id').val() +
	'&set_id=' + $('#set_id').val() +
	'&problem_id=' + $('#problem_id').val() +
	'&seed=' + $('#pg_seed').val() +
	'&hint_id=' + hints[idx].hint_id +
	'&teacher_id=' + $('#teacher_id').val() +
	'&port=' + $('#rest_port').val();
    window.open(url, '_blank');
}

function get_params() {
    if (QueryString.student_id) {
	$('#student_id').val(QueryString.student_id);
    }

    if (QueryString.teacher_id) {
	$('#teacher_id').val(QueryString.teacher_id);
    }

    if (QueryString.course_id) {
	$('#course_id').val(QueryString.course_id);
    }

    if (QueryString.set_id) {
	$('#set_id').val(QueryString.set_id);
    }

    if (QueryString.problem_id) {
	$('#problem_id').val(QueryString.problem_id);
    }

    if (QueryString.sockjs_port) {
	$('#sockjs_port').val(QueryString.sockjs_port);
    }

    if (QueryString.rest_port) {
	$('#rest_port').val(QueryString.rest_port);
    }
}

function parse_past_answers(answers, boxname, dtable) {
    dtable.fnClearTable();
    for (var i = 0; i < answers.length; i++) {
	if (answers[i].boxname == boxname) {
	    dtable.fnAddData([
		answers[i].timestamp.toString(),
		"<p class=\"timestamp\" value=\"" +
		    answers[i].timestamp.toString() +
		    "\"></p>",
		answers[i].entered_value,
		answers[i].is_correct]);
	}
    }
    dtable.fnSort([
	[0, 'desc']
    ]);
}

function update_timestamp() {
    var ts = Math.round((new Date()).getTime() / 1000);
    $('.timestamp').each(function() {
	$(this).html(secondsToString((ts - $(this).attr('value'))));
    });
}

function update_answer_tables(data) {
    $('#past_answers  table[id^=AnSwEr]').each(function() {
	var boxname = $(this).attr('id').split('_')[0];
	parse_past_answers(data.answers,
			   boxname,
			   $(this).dataTable());
    });
    update_timestamp();
}

function onRenderComplete(student_info) {
    // Create answer table for each answer box
    $('#problem_preview input[id^=AnSwEr]').each(function() {
	var boxname = $(this).attr('id');
	if (boxname != 'AnSwEr0001') {
	    $('#AnSwEr0001_table')
		.clone()
		.attr('id', boxname + '_table')
		.appendTo('#answer_container');
	}

	$('#hint_location')
	    .append($('<option>', { boxname : 'value' })
		    .text(boxname));
    });

    // Add table header
    $('#past_answers  table[id^=AnSwEr]').each(function() {
	$(this).dataTable({
	    'bPaginate': false,
	    'bSort': false,
	    'bInfo': false,
	    'bFilter': false,
	    'sScrollY': '120px',
	    "sDom": '<"header">frtip',
	    //"bAutoWidth": false,
	    "aoColumns": [
		/* timestamp */ { "sWidth": "0%",  "bVisible": false },
		/* sec. ago */  { "sWidth": "10%" },
		/* answer */ { "sWidth": "80%" },
		/* correct */  { "sWidth": "10%" }
	    ]
	});
	var this_id = $(this).attr('id');
	var table_title = this_id.replace("_table","");
	$('#' + this_id + '_wrapper div.header').html(table_title);
    });

    $('#problem_preview input[id^=AnSwEr]').each(function() {
	// get the boxname
	var boxid = $(this).attr('id');
	$(this).prop('readonly', true);
	// Add focus events
	$(this).focus(function() {
	    $('div[id$="_table_wrapper"]')
		.css('border','1px solid black');
	    var target_answer = $('div[id^="' + boxid +'"]');
	    target_answer.css('border','2px solid red');
	    var p = target_answer.offset().top;
	    var current_scroll = $('#past_answers').scrollTop();
	    var offset_top = $('#past_answers').offset().top;
	    $('#past_answers').scrollTop(p + current_scroll - offset_top);
	});

	// Add hint button
	var button = $('<button>+</button>')
	    .css({
		'color':'blue',
		'font-size':'14px',
		'font-weight':'bold'
	    })
	    .click(function() {
		$('#hint_location').val(boxid);
		$('#hint_container').show();
		window.scrollTo(0, document.body.scrollHeight);
	    });
	$(this).after(button);
    });


    // Show the page if everything loads correctly.
    $('#page_container').show();

    update_answer_tables(student_info);
    update_hints(student_info);
    update_answers(student_info);
}

function render_problem(student_info) {
    var post_data = {
	'pg_file': $('#pg_file').val(),
	'seed': $('#pg_seed').val()
    };
    $("#problem_preview").html('Rendering problem...');
    $.post(REST_SERVER + ':' + $('#rest_port').val() + '/render',
	   post_data,
	   function(r) {
	       var err = r.error_msg;
	       if (err && err.length > 0) {
		   $("#problem_preview").html(err);
	       } else {
		   $("#problem_preview").html(r.rendered_html);
	       }
	       onRenderComplete(student_info);
	   });
}


// Remove all displayed hints.
function remove_all_hints() {
    $('#problem_preview div[id^=wrapper_]').remove();
}

// Insert a hint to a given location.
function insert_hint(hint_html, location, hintbox_id) {
    hint_html = '<div style="float:right;">' +
	'<button onclick=remove_hint("'+ hintbox_id +
	'","' + location + '")>X</button></div>' + hint_html;
    var d = document.createElement('div');
    d.setAttribute('id', 'wrapper_' + hintbox_id);
    d.innerHTML = hint_html;
    d.setAttribute('style',
		   'background-color: #E0FAC0; ' +
		   'clear:left; ' +
		   'margin:10px; ' +
		   'border:1px solid; ' +
		   'padding:5px; ');
    $("#problem_preview input#" + location).before(d);
}


function update_hints(student_info) {
    remove_all_hints();
    for (var hint in student_info.hints) {
	if (student_info.hints.hasOwnProperty(hint)) {
	    var h = student_info.hints[hint];
	    insert_hint(h.hint_html,
			h.location,
			h.hintbox_id);
	}
    }
}


function update_answers(student_info) {
    for (var answer in student_info.answers) {
	if (student_info.answers.hasOwnProperty(answer)) {
	    var ans = student_info.answers[answer];
	    var box = $('#problem_preview input#'+ans.boxname);
	    box.val(ans.entered_value);
	    box.attr('title', 'Correct answer is ' + ans.correct_value);
	    if (ans.is_correct) {
		box.css('background-color', 'green');
	    } else {
		box.css('background-color', 'red');
	    }
	}
    }
}

function update_view(student_info) {
    if (window.rendered === undefined) {
	render_problem(student_info);
	window.rendered = true;
    }
    else {
	update_answer_tables(student_info);
	update_hints(student_info);
	update_answers(student_info);
    }
}

function parse_hints(dtable) {
    dtable.fnClearTable();
    for (var i = 0; i < hints.length; i++) {
	dtable.fnAddData([
	    hints[i].hint_id,
	    hints[i].pg_text,
	    hints[i].author,
	    "<button onclick=\"render_hint(" + i + 
		")\">Preview</button>" +
		"<button onclick=\"fork_hint(" + i + 
		")\">Fork</button>" + 
		"<button onclick=\"delete_hint(" + i + 
		")\">Delete</button>"]);
    }
}

function get_hints() {
    $.get(REST_SERVER + ':' + $('#rest_port').val() + '/problem_hints',
	  { 'course': $('#course_id').val(),
	    'set_id': $('#set_id').val(),
	    'problem_id': $('#problem_id').val()
	  }, function(data) {
	      hints = $.parseJSON(data);
	      var dtable = $('#hint_table').dataTable();
	      parse_hints(dtable);
	  });
}

// Request student info from server
function get_student_info() {
    send_command(sock, 'get_student_info', {
	'student_id': $('#student_id').val(),
	'course_id': $('#course_id').val(),
	'set_id': $('#set_id').val(),
	'problem_id': $('#problem_id').val()
    });
}

function timed_out() {
    $('#page_container').hide();
    $('#error_message').html('Hmm..the student has gone offline' +
			     '<br><button onclick="window.close()">' +
			     'Close</button>');
}

// Set up the SockJS connection
function setup_sockjs(port) {
    sock = new SockJS(REST_SERVER + ':' +
		      port + '/teacher');

    sock.onopen = function() {
	print("INFO: connected");
	send_command(sock, 'teacher_join', {
	    'teacher_id': $('#teacher_id').val(),
	    'student_id': $('#student_id').val(),
	    'course_id': $('#course_id').val(),
	    'set_id': $('#set_id').val(),
	    'problem_id': $('#problem_id').val()
	});
	get_student_info();
    };

    sock.onmessage = function(e) {
	print("RECIEVED: " + e.data);
	var data = $.parseJSON(e.data);
	if (data.type == 'student_info') {
	    var student_info = data['arguments'];
	    if ($.isEmptyObject(student_info)) {
		$('#add_hint').attr("disabled", "disabled");
		window.close_timer = setTimeout(function(){
		    timed_out();
		}, 60000);
	    }
	    else {
		if (window.close_timer !== undefined) {
		    clearTimeout(window.close_timer);
		}
		$('#add_hint').removeAttr('disabled');
		document.title = student_info.student_id +
		    '-' + student_info.set_id +
		    '-' + student_info.problem_id;
		$('#pg_file').val(student_info.pg_file);
		$('#pg_seed').val(student_info.pg_seed);
		$('#student_id').val(student_info.student_id);
		update_view(student_info);
	    }
	}
    };

    sock.onclose = function() {
	print("INFO: disconnected");
    };
}


//////////////////////////////////////////////////////

$(document).ready(function() {

    // Get url params
    get_params();

    // Set up SockJS
    setup_sockjs($('#sockjs_port').val());

    // Set up hint table
    $('#hint_table').dataTable({
	'bPaginate': false,
	'bInfo': false,
	'bFilter': false,
	"aoColumns": [
	    { "sWidth": "10%", "sClass": "center"  },
	    { "sWidth": "60%" },
	    { "sWidth": "10%" },
	    { "sWidth": "20%", "sClass": "center", "bSortable": false }]
    });

    // Get available hints
    get_hints();

    // Hide the preview box
    $('#hint_html').hide();

    $("#add_hint").click(function() {
	var location = $('#hint_location').val();
	if (location.length > 0 &&
	    hint_id !== undefined &&
	    hint_id !== null) {
	    send_command(sock, 'add_hint', {
		'student_id': $('#student_id').val(),
		'course_id': $('#course_id').val(),
		'set_id': $('#set_id').val(),
		'problem_id': $('#problem_id').val(),
		'location': $('#hint_location').val(),
		'hint_id': hint_id,
		'hint_html_template': $('#hint_html').html()
	    });
	}
	$("#cancel_hint").click();
    });

    $("#cancel_hint").click(function() {
	$('#hint_status').html('');
	$('#hint_html').hide();
	$('#hint_location').val('');
	hint_id = null;
	$('#hint_container').hide();
	window.scrollTo(0, 0);
    });

    $("#create_hint").click(function() {
	var url = 'hint_editor.html';
	url += '?course_id=' + $('#course_id').val() +
	    '&set_id=' + $('#set_id').val() +
	    '&problem_id=' + $('#problem_id').val() +
	    '&seed=' + $('#pg_seed').val() +
	    '&teacher_id=' + $('#teacher_id').val() +
	    '&port=' + $('#rest_port').val();
	window.open(url,'_blank');
    });

    $("#reload_hints").click(get_hints);

    // Auto send 'release_student' when closing window
    window.onbeforeunload = function() {
	console.log('what');
	send_command(sock, 'release_student', {
	    'student_id': $('#student_id').val(),
	    'course_id': $('#course_id').val(),
	    'set_id': $('#set_id').val(),
	    'problem_id': $('#problem_id').val()
	});
    };

    // Refresh timestamp every 5 sec.
    var ts_refresh = setInterval(update_timestamp, 5000);

    print("INFO: document loaded");
});
