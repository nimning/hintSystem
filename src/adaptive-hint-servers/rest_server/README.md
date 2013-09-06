## Directories and Files
- [rest_server.py](rest_server.py) -- Starts the ReSTful services.
- [pg_wrapper.py](pg_wrapper.py) -- Python interfaces to PG scripts.
- [render.py](render.py) -- Handler for ``/render``.
- [checkanswer.py](checkanswer.py) -- Handler for ``/checkanswer``.
- [scripts/renderPG.pl](scripts/renderPG.pl) -- Perl script for rendering a PG file.
- [scripts/checkanswer.pl](scripts/checkanswer.pl) -- Perl script for checking answers with a PG file.

## Interaction with PG
- Read [pg_wrapper.md](pg_wrapper.md)


## REST API Specification

#### PG Resources
  - ```POST /pg``` -- Retrieve PG source from a path 

#### Hint Resources
  - ```GET /hints/:pg_id``` -- Retrieve hints associated with the given pg_id
  - ```POST /hints/:pg_ig``` -- Add hints to the given pg_id
  - ```DELETE /hints/:hint_id``` -- Delete a hint

#### Render
  - ```POST /render``` -- Render HTML from PG
    - input: ```pg_file=/opt/webwork/.../sample.pg&seed=123```
    - JSON output: 

```javascript
{ 
  'rendered_html': '<div>Problem</div>' 
}
```

```
curl --data "pg_file=/opt/webwork/courses/UCSD_CSE103/templates/setAssignment6/BayesBurglary.pg&seed=5000" http://webwork.cse.ucsd.edu:4351/render
```


#### Check Answer
  - ``POST /checkanswer`` -- Check answers with PG
    - input: ``pg_file=/opt/webwork/.../sample.pg&seed=123&AnSwEr0001=42&AnSwEr0002=x``
    - JSON output: 

```javascipt
{ 
 'AnSwEr0001' : {
      'entered_value': '42',
      'correct_value': '42',
      'is_correct': true,
      'error_msg': ''
    },
 'AnSwEr0002' : {
      'entered_value': 'x',
      'correct_value': '12',
      'is_correct': false,
      'error_msg': 'Your answer isn\'t a number'
    }
}
```

```
curl --data "pg_file=/opt/webwork/courses/UCSD_CSE103/templates/setAssignment6/BayesBurglary.pg&seed=5000&AnSwEr0001=10" http://webwork.cse.ucsd.edu:4351/checkanswer
```
