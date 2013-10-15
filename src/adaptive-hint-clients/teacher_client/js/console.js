function get_params() {
    if (QueryString.sockjs_port) {
	$('#sockjs_port').val(QueryString.sockjs_port);
    }

    if (QueryString.rest_port) {
	$('#rest_port').val(QueryString.rest_port);
    }
}

// Open student_monitor page
function open_student_view(student_id, course_id, set_id, problem_id) {
    var url = "student_monitor.html?" +
	"teacher_id=" + $('#teacher_id').val() +
	"&student_id=" + student_id +
	"&course_id=" + course_id +
	"&set_id=" + set_id +
	"&problem_id=" + problem_id +
	"&sockjs_port=" + $("#sockjs_port").val() +
	"&rest_port=" + $("#rest_port").val();
    window.open(url, '_blank');
}

function take_student(student_id, course_id, set_id, problem_id) {
    send_command(sock, 'request_student',
		 {'student_id':student_id,
                  'course_id': course_id,
                  'set_id': set_id,
                  'problem_id': problem_id});
}

function release_student(student_id, course_id, set_id, problem_id) {
    send_command(sock, 'release_student',
		 {'student_id':student_id,
                  'course_id': course_id,
                  'set_id': set_id,
                  'problem_id': problem_id});
}

function add_rows_unassigned(stud_data) {
    var time_lastincorrect = Math.round(stud_data.time_lastincorrect / 60);
    var time_lasthint = Math.round(stud_data.time_lasthint / 60);
    var tries = stud_data.total_tries;
    var recent_tries = stud_data.recent_tries;
    var is_online = stud_data.is_online;

    // iconize
    if (is_online) is_online = '<img src="green.png">';
    else is_online = '<img src="gray.png">';


    // Already got correct answer, dont show.  
    if (time_lastincorrect === null) {
	return;
    }

    // Idle too long, dont show.
    if (time_lastincorrect > 10) {
	return;
    }

    // Not enough tries. Don't display on the table.
    if (tries === null || tries < 1) {
	//return;
    }

    // Add the row
    unassigned.fnAddData([stud_data.student_id,
                          stud_data.set_id,
                          stud_data.problem_id,
                          time_lastincorrect,
                          tries,
			  recent_tries,
			  is_online,
                          "<button id=take onclick=take_student('" +
                          stud_data.student_id + "','" +
                          stud_data.course_id + "','" +
                          stud_data.set_id + "','" +
                          stud_data.problem_id +
                          "')>Take</button>"]);
}


function add_row_my(stud_data) {
    var time_lastincorrect = Math.round(stud_data.time_lastincorrect / 60);
    var time_lasthint = Math.round(stud_data.time_lasthint / 60);
    var tries = stud_data.total_tries;
    var recent_tries = stud_data.recent_tries;
    var is_online = stud_data.is_online;
    var solved = stud_data.problem_solved;
    
    // iconize
    if (is_online) is_online = '<img src="green.png">';
    else is_online = '<img src="gray.png">';

    if (solved) solved = '<img src="green.png">';
    else solved = '<img src="gray.png">';
    
    // Add the row
    my.fnAddData([stud_data.student_id,
                  stud_data.set_id,
                  stud_data.problem_id,
                  time_lastincorrect,
                  tries,
		  recent_tries,
                  time_lasthint,
		  is_online,
		  solved,
                  "<button onclick=open_student_view('" +
                  stud_data.student_id + "','" +
                  stud_data.course_id + "','" +
                  stud_data.set_id + "','" +
                  stud_data.problem_id +
                  "')>View</button>" +
                  "<button onclick=release_student('" +
                  stud_data.student_id + "','" +
                  stud_data.course_id + "','" +
                  stud_data.set_id + "','" +
                  stud_data.problem_id +
                  "')>Unassign</button>"]);
}

function parse_unassigned(data) {
    unassigned.fnClearTable();
    for (var i = 0; i < data.length; i++) {
	var stud_data = data[i];
	add_rows_unassigned(stud_data);
    }
}

function parse_my(data) {
    my.fnClearTable();
    for (var i = 0; i < data.length; i++) {
	var stud_data = data[i];
	add_row_my(stud_data);
    }
}

//////////////////////////////////////////////

$(document).ready(function() {

    // Read URL params
    get_params();

    $("#after_login").hide();

    $('#login_button').click(function (){
	sock = new SockJS(SOCKJS_SERVER + ':' +
			  $('#sockjs_port').val() +
			  '/teacher');

	sock.onopen = function() {
	    print("INFO: connected");
	    teacher_id = $('#teacher_id').val();
	    send_command(sock, 'teacher_join',
			 { 'teacher_id' : teacher_id });
	};

	sock.onclose = function() {
	    print("INFO: disconnected");
	};

	sock.onmessage = function(e) {
	    print("RECIEVED: " + e.data);
	    data = jQuery.parseJSON(e.data);
	    if(data.type == "my_students") {
		parse_my(data["arguments"]);
	    }
	    else if (data.type=="unassigned_students") {
		parse_unassigned(data["arguments"]);
	    }
	};

	// Set UIs
	$("#login_button").hide();
	$("#teacher_id").hide();
	$("#teacher_id_label").html($("#teacher_id").val());
	$("#after_login").show();

	// Create tables
	unassigned = $('#unassigned_students').dataTable();
	my = $('#my_students').dataTable();

	// Set up refresh interval
	interval_id = window.setInterval(
	    function() {
		send_command(sock,'list_students',{});
	    }, 5000);
    });


    $('#logout_button').click(function () {
	clearInterval(interval_id);
	unassigned.fnClearTable();
	my.fnClearTable();

	$("#teacher_id_label").html("");
	$("#after_login").hide();
	$("#teacher_id").show();
	$("#login_button").show();
	sock.close();
    });

    $('#create_hint').click(function() {
	var url = "add_hint.html" +
	    "?teacher_id=" + $('#teacher_id').val() +
	    "&port=" + $('#rest_port').val();
	window.open(url, '_blank');
    });

});
