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
    var time_lastincorrect = stud_data.time_lastincorrect;
    var time_lasthint = stud_data.time_lasthint;
    var tries = stud_data.total_tries;
    var recent_tries = stud_data.recent_tries;
    var is_online = stud_data.is_online;

    // iconize
    if (is_online) is_online = '<img src="green.png" alt="online">';
    else is_online = '<img src="gray.png" alt="offline">';

    if (time_lasthint === null) {
	time_lasthint = '<span title="-1"></span>--';
    } else {
	time_lasthint = secondsToString(time_lasthint);
    }
 
    // Already got correct answer, dont show.  
    if (time_lastincorrect === null) {
	return;
    }

    // Not enough tries. Don't display on the table.
    if (tries === null || tries < 3) {
	return;
    }

    // Add the row
    unassigned.fnAddData([stud_data.student_id,
                          stud_data.set_id,
                          stud_data.problem_id,
                          secondsToString(time_lastincorrect),
                          tries,
			  recent_tries,
			  time_lasthint,
			  is_online,
                          "<button id=take onclick=take_student('" +
                          stud_data.student_id + "','" +
                          stud_data.course_id + "','" +
                          stud_data.set_id + "','" +
                          stud_data.problem_id +
                          "')>Take</button>"]);
}


function add_row_my(stud_data) {
    var time_lastincorrect = stud_data.time_lastincorrect;
    var time_lasthint = stud_data.time_lasthint;
    var tries = stud_data.total_tries;
    var recent_tries = stud_data.recent_tries;
    var is_online = stud_data.is_online;
    var solved = stud_data.problem_solved;
    
    // iconize
    if (is_online) is_online = '<img src="green.png" alt="online">';
    else is_online = '<img src="gray.png" alt="offline">';

    if (solved) solved = '<img src="green.png" alt="solved">';
    else solved = '<img src="gray.png" alt="unsolved">';

    if (time_lasthint === null) {
	time_lasthint = '<span title="-1"></span>--';
    } else {
	time_lasthint = secondsToString(time_lasthint);
    }
    
    // Add the row
    my.fnAddData([stud_data.student_id,
                  stud_data.set_id,
                  stud_data.problem_id,
                  secondsToString(time_lastincorrect),
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
    var oSettings = unassigned.fnSettings();
    var page = Math.floor(oSettings._iDisplayStart / oSettings._iDisplayLength);
    unassigned.fnClearTable();
    for (var i = 0; i < data.length; i++) {
	var stud_data = data[i];
	add_rows_unassigned(stud_data);
    }
    unassigned.fnPageChange(page);
    if (typeof(already_created_dropdown) === 'undefined') {
	/* Add a select menu for each TH element in the table footer */
	$("#course_filter").each( function () {
	    this.innerHTML = fnCreateSelect( unassigned.fnGetColumnData(1) );
	    $('select', this).change( function () {
		unassigned.fnFilter( $(this).val(), 1 );
	    } );
	} );
	already_created_dropdown = true;
    }
}

function parse_my(data) {
    var oSettings = my.fnSettings();
    var page = Math.floor(oSettings._iDisplayStart / oSettings._iDisplayLength);
    my.fnClearTable();
    for (var i = 0; i < data.length; i++) {
	var stud_data = data[i];
	add_row_my(stud_data);
    }
    my.fnPageChange(page);
}

//////////////////////////////////////////////

jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "title-numeric-pre": function ( a ) {
        var x = a.match(/title="*(-?[0-9\.]+)/)[1];
        return parseFloat( x );
    },
 
    "title-numeric-asc": function ( a, b ) {
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },
 
    "title-numeric-desc": function ( a, b ) {
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }
} );

jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "alt-string-pre": function ( a ) {
        return a.match(/alt="(.*?)"/)[1].toLowerCase();
    },
     
    "alt-string-asc": function( a, b ) {
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },
 
    "alt-string-desc": function(a,b) {
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }
} );

//////////////////////////////////////////////////



(function($) {
    /*
     * Function: fnGetColumnData
     * Purpose:  Return an array of table values from a particular column.
     * Returns:  array string: 1d data array 
     * Inputs:   object:oSettings - dataTable settings object. This is always the last argument past to the function
     *           int:iColumn - the id of the column to extract the data from
     *           bool:bUnique - optional - if set to false duplicated values are not filtered out
     *           bool:bFiltered - optional - if set to false all the table data is used (not only the filtered)
     *           bool:bIgnoreEmpty - optional - if set to false empty values are not filtered from the result array
     * Author:   Benedikt Forchhammer <b.forchhammer /AT\ mind2.de>
     */
    $.fn.dataTableExt.oApi.fnGetColumnData = function ( oSettings, iColumn, bUnique, bFiltered, bIgnoreEmpty ) {
	// check that we have a column id
	if ( typeof iColumn == "undefined" ) return new Array();
	
	// by default we only wany unique data
	if ( typeof bUnique == "undefined" ) bUnique = true;
	
	// by default we do want to only look at filtered data
	if ( typeof bFiltered == "undefined" ) bFiltered = true;
	
	// by default we do not wany to include empty values
	if ( typeof bIgnoreEmpty == "undefined" ) bIgnoreEmpty = true;
	
	// list of rows which we're going to loop through
	var aiRows;
	
	// use only filtered rows
	if (bFiltered == true) aiRows = oSettings.aiDisplay; 
	// use all rows
	else aiRows = oSettings.aiDisplayMaster; // all row numbers

	// set up data array	
	var asResultData = new Array();
	
	for (var i=0,c=aiRows.length; i<c; i++) {
	    iRow = aiRows[i];
	    var aData = this.fnGetData(iRow);
	    var sValue = aData[iColumn];
	    
	    // ignore empty values?
	    if (bIgnoreEmpty == true && sValue.length == 0) continue;

	    // ignore unique values?
	    else if (bUnique == true && jQuery.inArray(sValue, asResultData) > -1) continue;
	    
	    // else push the value onto the result data array
	    else asResultData.push(sValue);
	}
	
	return asResultData;
    }}(jQuery));


function fnCreateSelect( aData ) {
    var r='<select><option value=""></option>', i, iLen=aData.length;
    for ( i=0 ; i<iLen ; i++ ) {
	r += '<option value="'+aData[i]+'">'+aData[i]+'</option>';
    }
    return r+'</select>';
}

/////////////////////////////////////////////////////////


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
	    send_command(sock,'list_students',{});
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

    // Create tables
    unassigned = $('#unassigned_students').dataTable( {
        "aoColumns": [
            null,
            null,
	    null,
	    { "sType": "title-numeric" },
	    null,
	    null,
	    { "sType": "title-numeric" },
	    { "sType": "alt-string" },
	    null,
        ]
    } );

    my = $('#my_students').dataTable( {
        "aoColumns": [
            null,
            null,
	    null,
	    { "sType": "title-numeric" },
	    null,
	    null,
	    { "sType": "title-numeric" },
	    { "sType": "alt-string" },
	    { "sType": "alt-string" },
	    null,
        ]
    } );

});
