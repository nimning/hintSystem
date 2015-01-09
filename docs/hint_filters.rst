hint_filters package
====================

The hint_filters module was used in the previous iteration of hint filters,
where filters had to be defined ahead of time in the Python codebase. Filters in
this system are applied upon the server receiving a real-time (i.e. possibly
incomplete) answer from the student's client, and receive the following inputs:

        args is a dictionary containing the most recent attempt by a student
        to answer a question.  This contains user_id, hint_id, set_id, problem_id,
        and pg_id
        
        df is a pandas DataFrame storing the attempts by a student on a
        particular problem part where he/she is struggling
    
        previous_hint_assignments give a list of dictionaries, each dictionary
        containing at least user_id, set_id, problem_id, pg_id, hint_id
        giving the location where the hint has been previous assigned

If the hint filter returns true, the hint is assigned.

This API is pretty awkward and since it runs on real-time (partial) answers and
not actual student submissions, it was decided to scrap this and start from scratch.

Submodules
----------

.. toctree::

   hint_filters.AllFilters
   hint_filters.ExpressionFilters
   hint_filters.RegexMatchFilter
   hint_filters.StrugglingStudentFilter

Module contents
---------------

.. automodule:: hint_filters
    :members:
    :undoc-members:
    :show-inheritance:
