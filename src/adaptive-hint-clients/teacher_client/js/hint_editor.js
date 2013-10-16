function get_params() {
    if (QueryString.seed) {
	$('#seed').val(QueryString.seed);
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

    if (QueryString.hint_id) {
	$('#hint_id').val(QueryString.hint_id);
    }

    if (QueryString.teacher_id) {
	$('#teacher_id').val(QueryString.teacher_id);
    }

    if (QueryString.port) {
	$('#port').val(QueryString.port);
    }
}

function get_hint_by_hint_id() {
    $.get(REST_SERVER + ':' + $('#port').val() + '/hint', {
	'course': $('#course_id').val(),
	'hint_id': $('#hint_id').val()
    }, function (response) {
	var hint = $.parseJSON(response);
	hint_body.setValue(hint.pg_text);
    });
}

function initialize_codemirror() {
    hint_body = CodeMirror.fromTextArea(document.getElementById("hint_body"), {
	mode: "markdown",
	lineNumbers: true,
	styleActiveLine: true,
	matchBrackets: true
    });

    problem_pg = CodeMirror.fromTextArea(document.getElementById("problem_pg"), {
	mode: "perl",
	lineNumbers: true,
	readOnly: true
    });

    problem_pg.setSize('100%', 400);
    hint_body.setSize('100%', 400);
}


function render_problem(pg_text) {
    var post_data = {
	'pg_file': btoa(pg_text),
	'seed': $('#seed').val()
    };
    $.post(REST_SERVER + ':' + $('#port').val() + '/render',
           post_data,
           function (r) {
               var err = r.error_msg;
               if (err && err.length > 0) {
		   $("#problem_preview").html(err);
               } else {
		   var problem_html = r.rendered_html;
		   $("#problem_preview").html(problem_html);
               }
           });
}

function check_hint_answer() {
    var pg_text = (pg_header + '\n' +
                   hint_body.getValue() + '\n' +
                   pg_footer);
    var post_data = {
	'pg_file': btoa(pg_text),
	'seed': $('#seed').val()
    };
    post_data.AnSwEr0001 = $('#hint_preview #AnSwEr0001').val(); 
    $("#answer_status").val("Checking the answer...");
    $.post(REST_SERVER + ':' + $('#port').val() + "/checkanswer",
           post_data,
           function (r) {
               var err = r.error_msg;
               if (err && err.length > 0) {
		   $("#answer_status").val(err);
               } else {
		   $("#answer_status").val(JSON.stringify(r.AnSwEr0001));
               }
           });
}

function verify_hint(hint_html) {
    var box_count = 0;
    var answer_boxes = hint_html.match(/type=text/g);
    if (answer_boxes) {
	box_count = answer_boxes.length;
    }
    console.log(hint_html);
    console.log(answer_boxes);
    if (box_count > 1) {
	return "Each hint cannot have more than 1 answer box.";
    } 
    return "";
}

function render_hint() {
    var pg_text = (pg_header + '\n' +
                   hint_body.getValue() + '\n' +
                   pg_footer);
    var post_data = {
	'pg_file': btoa(pg_text),
	'seed': $('#seed').val()
    };
    $("#hint_preview").html("Rendering...");
    $.post(REST_SERVER + ':' + $('#port').val() + "/render",
           post_data,
           function (r) {
               var err = r.error_msg;
               if (err && err.length > 0) {
		   $("#hint_preview").html(err);
               } else {
		   // Clean up
		   var clean_html = r.rendered_html.replace(/[\s\S]*?<div/m, '<div').trim();
		   var verify_result = verify_hint(clean_html);
		   if (verify_result === "") {
		       $("#hint_preview").html(clean_html);
		   } else {
		       $("#hint_preview").html(verify_result);
		   }
               }
           });
}


function invalid_pg_file() {
    $('#container').hide();
    $('#error_report').html('Error: The PG file is not in PGML format.').show();
}


function load_pg() {
    $.get(REST_SERVER + ':' + $('#port').val() + '/pg_file', {
	'course': $('#course_id').val(),
	'set_id': $('#set_id').val(),
	'problem_id': $('#problem_id').val()
    }, function (response) {
	var pg_text = $.parseJSON(response);
	// Parse the pg text
	var re_header = /^[\s]*(TEXT\(PGML|BEGIN_PGML)[\s]+/gm;
	var re_footer = /^[\s]*END_PGML[\s]+/gm;
	pg_header = re_header.exec(pg_text);
	pg_footer = re_footer.exec(pg_text);
	var next_footer;
	while ((next_footer = re_footer.exec(pg_text)) != null) {
	    pg_footer = next_footer;
	}
	// check pgml format
	if (pg_header && pg_footer) {
	    // reconstruct the footer
	    pg_header = pg_text.substr(0, pg_header.index) + '\nBEGIN_PGML\n';
	    pg_footer = pg_text.substr(pg_footer.index);	    
	    // Remove Solution section
	    pg_footer = pg_footer.replace(/^(BEGIN_PGML_SOLUTION|BEGIN_PGML_HINT)[\s\S]*END_PGML_SOLUTION/m,'');
	    problem_pg.setValue(pg_text);
	    render_problem(pg_text);
	}
	else {
	    invalid_pg_file();
	}
    });
}

//////////////////////////////////////////////////////////////

$(function () {
    
    initialize_codemirror();
    get_params();
    load_pg();

    if ($('#hint_id').val().length > 0) {
	get_hint_by_hint_id();
    }

    $('#render').click(function () {
	render_hint();
    });

    $('#checkanswer').click(function() {
	check_hint_answer();
    });

    $('#save_hint').click(function() {
	var hint = {
	    'author': $('#teacher_id').val(),
	    'pg_text': hint_body.getValue().replace(/\\/g,"\\\\"),
	    'course': $('#course_id').val(),
	    'set_id': $('#set_id').val(),
	    'problem_id': $('#problem_id').val()
	};

	$.post(REST_SERVER + ':' + $('#port').val() + '/hint',
               hint,
               function(response) {
		   window.close();
               });
    });
});
