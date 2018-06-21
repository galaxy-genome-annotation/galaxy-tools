Galaxy-chado
=============

Galaxy tools to interface with Tripal using python-chado

Dependencies
------------

You will need to install some python modules in the Galaxy virtualenv for these
tools to be fully functional:

.. code:: bash

    . /path/to/galaxy/.venv/bin/activate
    pip install future chado
    deactivate

Environment
-----------

The following environment variables must be set:

+--------------------------------+-----------------------------------------------------------+
| ENV                            | Use                                                       |
+================================+===========================================================+
| ``$GALAXY_CHADO_DBHOST``       | Host of the Chado database                                |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_CHADO_DBNAME``       | Name of the Chado database                                |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_CHADO_DBUSER``       | Username to connect to the database                       |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_CHADO_DBPASS``       | Password to connect to the database                       |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_CHADO_DBSCHEMA``     | Database schema.                                          |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_CHADO_DBPORT``       | Port of the Chado database                                |
+--------------------------------+-----------------------------------------------------------+


License
-------

All python scripts and wrappers are licensed under MIT license.
