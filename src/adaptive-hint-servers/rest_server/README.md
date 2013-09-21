## Files
- [rest_server.py](rest_server.py) -- Start the ReSTful services.
- [pg_wrapper.py](pg_wrapper.py) -- Python interfaces to PG scripts.
- [checkanswer.py](checkanswer.py) -- Handler for `/checkanswer`.
- [render.py](render.py) -- Handler for `/render`.
- [hints_api.py](hints_api.py) -- Handler for `/user_problem_hints`, `/hint` and `/problem_hints`.
- [webwork.py](webwork.py) -- Handler for `/problem_seed`, `/pg_path` and `/pg_file`.
- [process_query.py](process_query.py) -- Base class for other RequestHandlers.
- [tornado_database.py](tonado_databse.py) -- Wrapper class for interfacing with MySQL.
- [webwork_config.py](webwork_config.py) -- Configuration file for the local WebWork installation.
- [scripts/renderPG.pl](scripts/renderPG.pl) -- Perl script for rendering a PG file.
- [scripts/checkanswer.pl](scripts/checkanswer.pl) -- Perl script for checking answers with a PG file.

## Interaction with PG
- Read [pg_wrapper.md](pg_wrapper.md)

## ReSTful APIs

### WebWork Resources
<table>
  <tr>
    <th>Request</th>
    <th>Parameters</th>
    <th>Response</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>
<code>
GET /pg_path
</code>
    </td>
    <td>
<pre>
{ 
 'course': 'demo',
 'set_id': 'sandbox',
 'problem_id': 1 
}
</pre>
    </td>
    <td>
<pre>
"/path/to/file.pg"
</pre>
    </td>
    <td>
      Get the path to the PG file.  
    </td>
  </tr>
  <tr>
    <td>
<code>
GET /pg_file
</code>
    </td>
    <td>
<pre>
{ 
 'course': 'demo',
 'set_id': 'sandbox',
 'problem_id': 1 
}
</pre>
    </td>
    <td>
<pre>
"DOCUMENT();....ENDDOCUMENT();"
</pre>
    </td>
    <td>
      Get the content of a PG file.
    </td>
  </tr>
  <tr>
    <td>
<code>
GET /problem_seed
</code>
    </td>
    <td>
<pre>
{ 
 'course': 'demo',
 'set_id': 'sandbox',
 'problem_id': 1,
 'user_id': 'scheaman'
}
</pre>
    </td>
    <td>
<pre>
2250
</pre>
    </td>
    <td>
      Get the random seed used by WebWork.
    </td>
  </tr>
</table>


## Rendering Services
<table>
  <tr>
    <th>Request</th>
    <th>Parameters</th>
    <th>Response</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>
<code>
POST /render
</code>
    </td>
    <td>
<pre>
{ 
 'pg_file': '/path/to/file.pg',
 'seed': 1234 
}

or

{ 
 'pg_file': {BASE64 pg text},
 'seed': 1234 
}
</pre>
    </td>
    <td>
<pre>
{ 
 'rendered_html': '&lt;html&gt;
    ...
    &lt;/html&gt;'
}
</pre>
    </td>
    <td>
      Render a given PG file.
    </td>
  </tr>
  <tr>
    <td>
<code>
POST /checkanswer
</code>
    </td>
    <td>
<pre>
{ 
 'pg_file': '/path/to/file.pg',
 'seed': 1234,
 'AnSwEr0001': '15!',
 'AnSwEr0002': 'x'
}

or

{ 
 'pg_file': {BASE64 pg text},
 'seed': 1234,
 'AnSwEr0001': '15!',
 'AnSwEr0002': 'x'
}

</pre>
    </td>
    <td>
<pre>
{ 
 'AnSwEr0001' : {
   'entered_value': '15!',
   'is_correct': true,
   'error_msg': ''
   },
 'AnSwEr0002' : {
   'entered_value': 'x',
   'is_correct': false,
   'error_msg': 
    'Answer isn\'t a number'
   }
}
</pre>
    </td>
    <td>
      Check answers with a PG file.
    </td>
  </tr>
</table>
  
### Hint Resources
<table>
  <tr>
    <th>Request</th>
    <th>Parameters</th>
    <th>Response</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>
<code>
GET /user_problem_hints
</code>
    </td>
    <td>
<pre>
{
 'course': 'demo',
 'set_id': 'sandbox',
 'problem_id': 2,
 'user_id': 'melkherj' 
}
</pre>
    </td>
    <td>
<pre>
[
 {
  'hint_id': 1234,
  'pg_text': 'Hint text',
  'pg_header': 'DOCUMENT(); ... ',
  'pg_footer': '... ENDDOCUMENT();',
  'pg_id': 'b',
  'hint_location': 'AnSwEr0001'
 }
]
</pre>
    </td>
    <td>
      Get hints assigned to a user for a particular problem.
    </td>
  </tr>
  <tr>
    <td>
<code>
GET /hints
</code>
    </td>
    <td>
<pre>
{
 'course': 'demo',
 'hint_id': '1234'
}
</pre>
    </td>
    <td>
<pre>
{
 "hint_id": 1234,
 "pg_text": "My name is Mr Hint", 
 'pg_header': 'DOCUMENT(); ... ',
 'pg_footer': '... ENDDOCUMENT();'
 "pg_id": "b", 
 "problem_id": "2"
 "set_id": "compoundProblemExperiments"
}
</pre>
    </td>
    <td>
      Get a hint from the hint DB.
    </td>
  </tr>
  <tr>
    <td>
<code>
POST /hints
</code>
    </td>
    <td>
<pre>
{
 'course': 'demo', 
 'pg_id': "b",
 'set_id': "compoundProblemExperiments",
 'problem_id' : '2',
 'pg_text': 'What is [`x^2+4x+2`]?',
 'pg_header': 'DOCUMENT(); ... ',
 'pg_footer': '... ENDDOCUMENT();'
}
</pre>
    </td>
    <td>
<pre>
None
</pre>
    </td>
    <td>
      Add a hint to the hint DB.
    </td>
  </tr>
   <tr>
    <td>
<code>
GET /problem_hints
</code>
    </td>
    <td>
<pre>
{
 'course': 'demo', 
 'set_id': "compoundProblemExperiments",
 'problem_id' : '2',
}
</pre>
    </td>
    <td>
<pre>
[
 {
  'hint_id': 123,
  "pg_text": "My name is Mr Hint",
  'pg_header': 'DOCUMENT(); ... ',
  'pg_footer': '... ENDDOCUMENT();'
  "pg_id": "b"
 },...
]
</pre>
    </td>
    <td>
      List all hints for a problem.
    </td>
  </tr>
</table>
