$(document).ready(function(){

var default_part_init_time = 1000;
var default_part_display_time = 5000;
var char_time_interval = 200; 
var timer_seconds = 0;
var current_cluster = {};

function format_number_length(num, length) {
    var r = "" + num;
    while (r.length < length) {
        r = "0" + r;
    }
    return r;
}

function keys(obj)
{
    var keys = [];
    for(var key in obj)
    {
        if(obj.hasOwnProperty(key))
        {
            keys.push(key);
        }
    }

    return keys;
}

function send_receive_json(data, handle_response) {
    // sends a json object to the web server, parses the json object 
    //   returned
    
    // abort any pending request
    if (request) {
       request.abort();
    }
    var json_data = JSON.stringify(data, null, 2);

    // fire off the request
    var request = $.ajax({
        url: "",
        type: "post",
        data: json_data
    });
    // callback handler that will be called on success
    request.done(function (response, textStatus, jqXHR){
        // log a message to the console
        handle_response(response);
    });
    // callback handler that will be called on failure
    request.fail(function (jqXHR, textStatus, errorThrown){
        // log the error to the console
        console.error(
            "The following error occured: "+
            textStatus, errorThrown
        );
    });

}
/*
function handle_server_response(response_str, init) {
    parts_info = JSON.parse(response_str);
    sorted_keys = keys(parts_info).sort();
    for (var i=0; i<sorted_keys.length; i++) {
        //Define useful variables
        info = parts_info[i];
        var part_id = "part"+i
        var part = $("#"+part_id)
        var answerbox = $("#"+part_id+" .answerbox")
        var tip = $("#tip"+part_id)

        //Disable all tooltips
        //answerbox.tooltip({disabled: true});
        
        if (info['visible']) {
            part.show();
            answerbox.tooltip({disabled:true});
            if (info['hint']) {
                answerbox.tooltip({disabled:false});
                //answerbox.attr("title",info['hint']);
                if (!info['correct']){
                    tip.html(info['hint'])
                    tip.slideDown();
                }
            }
            else{
                tip.slideUp();
            }
            //color correct/incorrect parts accordingly
            if (info["correct"]) {
                answerbox.css("background-color", "#88ff88"); //green
                tip.slideUp();
            }
            else {
                answerbox.css("background-color", "#ff9494"); //red
            }
        }
        else {
            part.hide();
        } 
            
    }
    return
    for (var subpart in subpart_hints) {
        $("#"+subpart).tooltip({disabled:false})
        $("#"+subpart).attr("title",subpart_hints[subpart]);
    }
    for (var part in parts_hidden) {
        if (parts_hidden[part]) {
            $('#'+part).hide();
        }
        else {
            $('#'+part).show();
        } 
    }
}
*/
/*
function get_part_exprs() { 
    // Get expressions corresponding to subparts (text boxes)
    var exprs = [];
    $(".answerbox").each(function(index){
        exprs[index] = $(this).val();
    })
    return exprs;
}
*/

function synchronize_with_server() {
    //exprs = get_part_exprs();
    //send_receive_json(exprs, handle_server_response);
    send_receive_json("", change_every_five_seconds);
}

/*
$(".answerbox").keyup(function(event){
    //synchronize_with_server();
});
*/

synchronize_with_server();

function change_every_five_seconds(response_str, init){
    parts_info = JSON.parse(response_str);
    //hide all parts and tips to begin
    $(".part").hide();  
    $(".tip").hide();  
    display_hashmap(0, parts_info);
}

function display_hashmap(part_index, parts_info){
    //Change the show and hide sections
    if (part_index >= parts_info.length) {
        return;
    }
    info = parts_info[part_index];
    for (var i=0; i<info["show"].length; i++) {
        part_id = info["show"][i];
        var part = $("#part"+part_id);
        part.slideDown();
    }
    for (var i=0; i<info["hide"].length; i++) {
        part_id = info["hide"][i];
        var part = $("#part"+part_id);
        part.hide();
    }
    var part = "part"+info["part"];
    var answerbox = $("#"+part+" .answerbox");
    answerbox.css("background-color","#D6D6F3"); //Light grey
    expr = '' + info["expr"]; 
    expr_display_time = char_time_interval*expr.length;
    if (info["timedelta"] == 0) {
        part_display_time = expr_display_time;
        part_init_time = 0;
    }
    else {
        part_display_time = Math.max(default_part_display_time, expr_display_time);
        part_init_time = default_part_init_time;
    }
    //var char_time_interval = Math.round(part_display_time/expr.length);
    //Display part correctness after expression is entered
    setTimeout(
        function() {
            if (info["correct"]) {
                answerbox.css("background-color", "#88ff88"); //green
            }
            else {
                answerbox.css("background-color", "#ff9494"); //red
            }
        },
        part_init_time + part_display_time
    );
    // Wait part_init_time, then display the expression 
    // character-by-character in time intervals char_time_interval
    setTimeout(
        function(){
            answerbox.focus()
            display_expr(expr,answerbox,char_time_interval)
        },
        part_init_time+part_display_time-expr_display_time);
    setTimeout(
        function(){run_attempt_timer(info["timedelta"], part_display_time)},
        part_init_time);

    // Wait, then display the next student attempt
    function display_hashmap_bound() {
        display_hashmap(part_index+1,parts_info);
    }
    setTimeout(display_hashmap_bound,2*part_init_time + part_display_time);
}

function display_expr(expr,answerbox,time_per_char){
    //make sure variable expration is string, have the charAt() function
    var expration = expr+"";
    var it=0;
    var t;
    answerbox.val(""); //Reset answerbox expression
    function reveal_expr_by_char(){
        current_text = answerbox.val();
        answerbox.val(current_text+expration.charAt(it));
        if ( it < expration.length - 1){
            it++;
            t = setTimeout(reveal_expr_by_char,time_per_char);
        }
        else{
            clearTimeout(t);
        }
    }
    reveal_expr_by_char(); 
}


function run_attempt_timer(timedelta, part_display_time){
    // timedelta is the time the student took in webwork to answer the problem
    //   part currently being displayed

    // time_interval is the browser-time to spend for each one-second increment
    //   of the timer
    var time_interval = part_display_time/timedelta
    function increment_ui_timer(seconds_increment) {
        timer_seconds = timer_seconds + seconds_increment;
        // Update the timer with the given number of seconds
        MMSS = format_number_length(Math.floor(timer_seconds/60),2) + ':'+ 
            format_number_length(timer_seconds%60,2);
        $("#wrap #timedelta").html(MMSS);
    }
    var t = 0;
    function update_counter(){
        if (t < timedelta) {
            increment_ui_timer(1)
            t++;
            setTimeout(update_counter, time_interval);
        }
    }
    update_counter()
}

});

