Galaxy-tripal
=============

Galaxy tools to interface with Tripal using python-tripal

Dependencies
------------

You will need to install some python modules in the Galaxy virtualenv for these
tools to be fully functional:

.. code:: bash

    . /path/to/galaxy/.venv/bin/activate
    pip install future tripal
    deactivate

Environment
-----------

The following environment variables must be set:

+--------------------------------+-----------------------------------------------------------+
| ENV                            | Use                                                       |
+================================+===========================================================+
| ``$GALAXY_TRIPAL_URL``         | The URL at which Tripal is accessible, internal to Galaxy |
|                                | and where the tools run. Must be absolute, with FQDN and  |
|                                | protocol.                                                 |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_TRIPAL_USER``        | The admin user which Galaxy should use to talk to Tripal. |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_TRIPAL_PASSWORD``    | The password for the admin user.                          |
|                                |                                                           |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_TRIPAL_SHARED_DIR``  | Directory shared between Galaxy and Tripal, used to       |
|                                | exchange data files.                                      |
+--------------------------------+-----------------------------------------------------------+


License
-------

All python scripts and wrappers are licensed under MIT license.
