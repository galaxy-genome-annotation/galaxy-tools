Galaxy-apollo
=============

Galaxy tools to interface with Apollo.
Uses `python-apollo <https://github.com/galaxy-genome-annotation/python-apollo>`__ for most of it.

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

As an alternative to ``$GALAXY_WEBAPOLLO_URL``, ``$GALAXY_WEBAPOLLO_USER`` and ``$GALAXY_WEBAPOLLO_PASSWORD``, you can
define ``ARROW_GLOBAL_CONFIG_PATH`` with the path to a python-apollo/arrow conf file.

License
-------

All python scripts, wrappers, and the webapollo.py are licensed under
MIT license.
