rest_server package
===================

The REST server is an HTTP server which serves as the main API for the
Adaptive Hints system. It provides access to information from the
Webwork MySQL database, renders and checks answers to Webwork problems
in PG file format, allows CRUD operations on hints, runs filters on
student answers to perform automatic hint assignment, and performs
other types of analytics on student performance.

The REST server is a standard HTTP request-response server. It has
access to the Webwork MySQL database (which includes hint-related
tables), and also Webwork itself via XMLRPC calls. Request parameters
can be formatted as JSON, or as GET parameters or form fields
depending on the type of request. It *does not* have access to current
student sessions, so the SockJS server must be used for any real time
communication purposes.

The REST server is built using Tornado Web, an asynchronous processing
framework. The list of entry points/possible requests is in
the rest_server module, and the different request handlers are in the other
classes in this package.

Subpackages
-----------

.. toctree::

    rest_server.hint_filters

Submodules
----------

.. toctree::

   rest_server.auth
   rest_server.checkanswer
   rest_server.convert_timestamp
   rest_server.exec_filters
   rest_server.filter_api
   rest_server.get_answers
   rest_server.get_header_footer
   rest_server.hints_api
   rest_server.json_request_handler
   rest_server.parsers
   rest_server.parsetab
   rest_server.pg_utils
   rest_server.pg_wrapper
   rest_server.process_query
   rest_server.render
   rest_server.rest_server
   rest_server.scratch
   rest_server.webwork
   rest_server.webwork_config
   rest_server.webwork_utils

Module contents
---------------

.. automodule:: rest_server
    :members:
    :undoc-members:
    :show-inheritance:
