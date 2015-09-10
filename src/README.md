# Student Adaptive Server #

## Installation ##

You should have two folders: the source and data folders.  These are two distinct git repositories and directories to allow for separate versioning of source and data.  
Add the following to your .profile, .bashrc, or some script that is run on terminal startup:

    PYTHONPATH=$PYTHONPATH:<path to source root>
Change the value of `"Data path"` in `<source root>/config.yaml` to the root directory where you extracted the webwork/student adaptive server data. 

## Rendering HTML and Running ##
    cd <source root>/student_adaptive_server
    ./render.py; ./server.py

_Note_: You'll probably realize when running `./render.py; ./server.py` that you're missing some python packages.  These include ply, numpy/scipy, scikit-learn, and nltk.  Install them.  

## Important Source and Data Files ##
The source files you probably care about when making modifications to the student server are in `<source root>/student_adaptive_server`.  These files are:

* `client_template.html`: The html file to send to the client, without a body. 
* `client.js`: The client logic
* `render_html.py`: A script that takes `client_template.html` as a base, `.../parts0_7.json` for problem data, and generates client.html to be served up 
* `server.py`: The server.  It initially sends client.html, then allows communication with the client through POST requests

The data files you probably care about modifying are in `<data root>/student_adaptive_server`:

* `parts0_7.json` Problem and hint text, answers, expression clusters, and problem part dependency information.  
* `hard_parts.json` An array of sessions where students struggled.  Each session is an array of student attempts, each attempt a dictionary describing how long the student took, what expression the student entered, whether the student was correct, and other info.  
* `hard_parts_with_hints.json` How we imagine the student sessions in `hard_parts.json` would go if the students were given hints.  

Also take a look at `config.yaml`, which provides a number of parameters to render.py and server.py
