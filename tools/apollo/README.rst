Galaxy-apollo
=============

Galaxy tools to interface with Apollo The webapollo.py file is also
`separately
available <https://github.com/galaxy-genome-annotation/python-apollo>`__
as a pip-installable package.

Environ

The following environment variables must be set:

+----------------+-----------------------------------------------------------+
| ENV            | Use                                                       |
+================+===========================================================+
| ``$GALAXY_WEBA | The URL at which Apollo is accessible, internal to Galaxy |
| POLLO_URL``    | and where the tools run. Must be absolute, with FQDN and  |
|                | protocol.                                                 |
+----------------+-----------------------------------------------------------+
| ``$GALAXY_WEBA | The admin user which Galaxy should use to talk to Apollo. |
| POLLO_USER``   |                                                           |
+----------------+-----------------------------------------------------------+
| ``$GALAXY_WEBA | The password for the admin user.                          |
| POLLO_PASSWORD |                                                           |
| ``             |                                                           |
+----------------+-----------------------------------------------------------+
| ``$GALAXY_WEBA | The external URL at which Apollo is accessible to end     |
| POLLO_EXT_URL` | users. May be relative or absolute.                       |
| `              |                                                           |
+----------------+-----------------------------------------------------------+
| ``$GALAXY_SHAR | Directory shared between Galaxy and Apollo, used to       |
| ED_DIR``       | exchange JBrowse instances.                               |
+----------------+-----------------------------------------------------------+

License
-------

All python scripts, wrappers, and the webapollo.py are licensed under
MIT license.
