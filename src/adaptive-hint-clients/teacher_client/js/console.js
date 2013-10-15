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

function parse_hints (hints) {
  var len = hints.length;
  if (len > 0) {
    var d = new Date();
    var time_temp = (Math.round(d.getTime()/1000) -
                     hints[len-1].timestamp)/(60);

    var min = Math.floor(time_temp);
    //var sec = Math.floor((time_temp%1)*60);

    var time_lasthint = min;

    if (time_lasthint > 10) {
      time_lasthint = '>10';
    }

    return time_lasthint;
  }
  else {
    return 0;
  }
}

// Calculate time spent in minutes
// Returns: time spent in minutes
function calc_time_spent(past_answers, part) {
  var len = past_answers.length;
  var sum_time = 0;
  for (var i = len-1; i >= 1; i--) {
    if (past_answers[i].boxname == part) {
      sum_time += past_answers[i].timestamp - past_answers[i-1].timestamp;
      //print("sum="+sum_time);
    }
  }
  var time_spent_temp = (Math.round(new Date().getTime()/1000) +
                         sum_time - past_answers[len-1].timestamp)/(60);

  //print(new Date().getTime()/1000);
  //print(sum_time);
  //print(past_answers[len-1].timestamp);
  //print(time_spent_temp);

  return Math.round(time_spent_temp);
}

// Calculate the number of tries
// Returns: number of tries or null if correct answer was given.
function calc_tries(past_answers, part) {
  var len = past_answers.length;
  var tries = 0;
  for (var j = len-1; j>=0; j--) {
    if (past_answers[j].boxname == part) {
      tries++;
    }
  }
  return tries;
}

function calc_recent_tries(past_answers, part) {
  var len = past_answers.length;
  var tries = 0;
  // 15 mins
  var time_window = (new Date().getTime()/1000.0) - (15 * 60);
  for (var j = len-1; j>=0; j--) {
    if (past_answers[j].boxname == part &&
        past_answers[j].timestamp > time_window) {
      tries++;
    }
  }
  return tries;
}


// Returns null if the last answer is correct
function calc_time_lastincorrect(past_answers, part) {
  var len = past_answers.length;
  var time_lastincorrect = 0;
  for (var j = len-1; j>=0; j--) {
    if (past_answers[j].is_correct === false &&
        past_answers[j].boxname == part) {
      var time_temp = (Math.round(new Date().getTime()/1000) -
                       past_answers[j].timestamp)/(60);
      //print(new Date().getTime()/1000 +" "+ past_answers[len-1].timestamp);
      time_lastincorrect = Math.round(time_temp);
      return time_lastincorrect;
    }
  }  
  return null;
}


function add_row_my(stud_data) {
  var past_answers = stud_data.answers;
  var len = past_answers.length;

  // Answers are empty. Don't display in the table.
  if (len === 0) {
    return;
  }

  var part = past_answers[len-1].boxname;
  var time_lastincorrect = calc_time_lastincorrect(past_answers, part);
  var time_lasthint = parse_hints(stud_data.hints);
  var tries = calc_tries(past_answers, part);
  var recent_tries = calc_recent_tries(past_answers, part);

  // Don't show if the current part is completed
  if (time_lastincorrect === null) {
    return;  
  }

  if (time_lastincorrect > 10) {
    return;
    //time_lastincorrect = '>10';
  }

  // Add the row
  my.fnAddData([stud_data.student_id,
                time_lastincorrect,
                stud_data.set_id,
                stud_data.problem_id,
                parseInt(part.substr(6), 10).toString(),
                tries,
		recent_tries,
                time_lasthint,
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


function add_rows_unassigned(stud_data) {
  var past_answers = stud_data.answers;
  var len = past_answers.length;

  // Answers are empty. Don't display in the table
  if (len === 0) {
    return;
  }

  // Find out part names
  var all_parts = {};
  for (var ii = 0; ii < len; ii++) {
    all_parts[past_answers[ii].boxname] = (
      past_answers[ii].boxname.substr(6));
  }

  for (var part in all_parts) {
    var tries = calc_tries(past_answers, part);
    var recent_tries = calc_recent_tries(past_answers, part);
    var time_lastincorrect = calc_time_lastincorrect(past_answers, part);
    
    // Already got correct answer, dont show.  
    if (time_lastincorrect === null) {
      continue;
    }

    // Idle too long, dont show.
    if (time_lastincorrect > 10) {
      continue;
      //time_lastincorrect = '>10';
    }

    // Not enough tries. Don't display on the table.
    if (tries === null || tries < 1) {
      continue;
    }

    // Add the row
    unassigned.fnAddData([stud_data.student_id,
                          time_lastincorrect,
                          stud_data.set_id,
                          stud_data.problem_id,
                          parseInt(part.substr(6), 10).toString(),
                          tries,
			  recent_tries,
                          "<button id=take onclick=take_student('" +
                          stud_data.student_id + "','" +
                          stud_data.course_id + "','" +
                          stud_data.set_id + "','" +
                          stud_data.problem_id +
                          "')>Take</button>"]);
  }
}


function parse_my(data) {
  my.fnClearTable();
  for (var i = 0; i < data.length; i++) {
    var stud_data = data[i];
    add_row_my(stud_data);
  }
}

function parse_unassigned(data) {
  unassigned.fnClearTable();
  for (var i = 0; i < data.length; i++) {
    var stud_data = data[i];
    add_rows_unassigned(stud_data);
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
