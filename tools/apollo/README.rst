Galaxy-apollo
=============

Galaxy tools to interface with Apollo The webapollo.py file is also
`separately
available <https://github.com/galaxy-genome-annotation/python-apollo>`__
as a pip-installable package.

Dependencies
------------

You will need to install some python modules in the Galaxy virtualenv for these
tools to be fully functional:

.. code:: bash

    . /path/to/galaxy/.venv/bin/activate
    pip install six biopython bcbio-gff
    deactivate

Environment
-----------

The following environment variables must be set:

+--------------------------------+-----------------------------------------------------------+
| ENV                            | Use                                                       |
+================================+===========================================================+
| ``$GALAXY_WEBAPOLLO_URL``      | The URL at which Apollo is accessible, internal to Galaxy |
|                                | and where the tools run. Must be absolute, with FQDN and  |
|                                | protocol.                                                 |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_USER``     | The admin user which Galaxy should use to talk to Apollo. |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_PASSWORD`` | The password for the admin user.                          |
|                                |                                                           |
|                                |                                                           |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_WEBAPOLLO_EXT_URL``  | May be relative or absolute.                              |
|                                | The external URL at which Apollo is accessible to end     |
|                                | users.                                                    |
+--------------------------------+-----------------------------------------------------------+
| ``$GALAXY_SHARED_DIR``         | Directory shared between Galaxy and Apollo, used to       |
|                                | exchange JBrowse instances.                               |
+--------------------------------+-----------------------------------------------------------+

License
-------

All python scripts, wrappers, and the webapollo.py are licensed under
MIT license.
