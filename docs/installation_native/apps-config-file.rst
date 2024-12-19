Create Application Mapping File
===============================

Since a single BYCEPS instance can provide the admin frontend, the API,
*and* one or more sites, a configuration file is required that defines
which hostname will be routed to which application.

Copy the included example configuration file:

.. code-block:: sh

    $ cp config/apps.toml.example config/apps.toml

- For a **local installation**, you can go with the exemplary hostnames
  already defined in the example apps configuration file,
  :file:`config/apps.toml.example`, which are:

  - ``admin.byceps.example`` for the admin UI
  - ``api.byceps.example`` for the API
  - ``cozylan.example`` for the CozyLAN demo site

  To be able to access them, though, add these entries to your local
  :file:`/etc/hosts` file (or whatever the equivalent of your operating
  system is):

  .. code-block::

      127.0.0.1       admin.byceps.example
      127.0.0.1       api.byceps.example
      127.0.0.1       cozylan.example

- But if you are **installing to a server on the Internet**, substitute
  above hostnames in the configuration with ones that use actual,
  registered Internet domains.
