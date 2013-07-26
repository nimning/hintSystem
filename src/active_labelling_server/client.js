$(document).ready(function(){

var labelled_examples;

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

function update_example_label(example_index, label) {
    example = $('#example'+example_index)
    labelled_examples[example_index]['label'] = label;
    if (label == 1) {
        example.css("color", 'green'); //green
    }
    else {
        example.css("color", 'red'); //red
    }
}

function flip_example_label(example_index) {
    // Switch example labels 0 -> 1, and 1 -> 0
    update_example_label(example_index, 
        1 - labelled_examples[example_index]['label']);
}

function load_examples(response_str, init) {
    labelled_examples = JSON.parse(response_str);
    $('#labelled_examples').empty();
    for (var i=0;i<labelled_examples.length;i++) {
        // Add example to page
        example_html = labelled_examples[i]['example'];
        label = labelled_examples[i]['label']; 
        $('#labelled_examples').append(
            '<p id="example'+i+'">'+example_html+'</p>' )
        // Register example label: change color and data structure
        update_example_label(i, label)
        // Register 'flip label' event for each example, upon a click
        $("#example"+i).click(function(){
            index = this.id.charAt(this.id.length-1);
            flip_example_label(index);
        })
    }
}

send_receive_json([], load_examples);

$("#next_batch_button").click(function(){
    labels = labelled_examples.map(function(x){return x['label']})
    send_receive_json(labels,load_examples);
})
$("#done_button").click(function(){
    send_receive_json({},load_examples);
})
 
});

