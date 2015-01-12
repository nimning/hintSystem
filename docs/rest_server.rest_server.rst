rest_server.rest_server module
==============================

The rest_server script runs the REST Server. It handles several
possible requests, which are listed in the code listing below. The
actual request handlers are defined by classes in the other file in
this package.

.. literalinclude:: /../src/adaptive-hint-servers/rest_server/rest_server.py
   :start-after: # Request handlers
   :end-before: # Server configuration

.. literalinclude:: /../src/adaptive-hint-servers/rest_server/rest_server.py
   :start-after: # Application server
   :end-before: # Start server

.. automodule:: rest_server.rest_server
    :members:
    :undoc-members:
    :show-inheritance:
