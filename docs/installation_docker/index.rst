*****************************
Installation (Docker Compose)
*****************************

As an alternative to :doc:`installing directly on a system
</installation_native/index>`, BYCEPS can be run from Docker_ containers,
orchestrated by `Docker compose`_.

.. important:: This guide assumes you are using Docker Compose V2. If you are
   still using V1, replace ``docker compose`` with ``docker-compose`` before
   running commands that include it.

Since there is no official Docker image for BYCEPS at this point, you have to
build one yourself.

.. _Docker: https://www.docker.com/
.. _Docker Compose: https://docs.docker.com/compose/


Obtain BYCEPS
=============

First, clone BYCEPS' Git repository to your machine:

.. code-block:: console

    $ git clone https://github.com/byceps/byceps.git

A new directory, :file:`byceps/`, should have been created. ``cd`` into it.


Create BYCEPS Configuration File
================================

To run BYCEPS, a configuration file is required. Create a copy of the example
file for the Docker setup:

.. code-block:: console

    $ cp docker/byceps/config.toml.example docker/byceps/config.toml


Set a Secret Key
----------------

A secret key is, among other things, required for login sessions. So let's
generate one in a cryptographically secure way:

.. code-block:: console

    $ docker compose run --rm byceps-apps uv run byceps generate-secret-key

Exemplary output:

.. code-block:: none

    3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293

Set this value in your configuration file so the line looks like this:

.. code-block:: toml
    :caption: excerpt from :file:`docker/byceps/config.toml`

    secret_key = "3ac1c416bfacb82918d56720d1c3104fd96e8b8d4fbee42343ae7512a9ced293"

.. attention:: Do **not** use the above key (or any other key you copied from
   anywhere). Generate **your own** secret key!

.. attention:: Do **not** use the same key for development and production
   environments. Generate **separate** secret keys!


Hostname-to-Application Routing
===============================

Since a single BYCEPS instance can provide the admin frontend, the API, *and*
one or more sites, a configuration is required that defines which hostname will
be routed to which application. This is done in the ``[apps]`` section in the
configuration file.

- For a **local installation**, you can go with the exemplary hostnames already
  defined in the example configuration file,
  :file:`docker/byceps/config.toml.example`, which are:

  - ``admin.byceps.example`` for the admin UI
  - ``api.byceps.example`` for the API
  - ``cozylan.example`` for the CozyLAN demo site

  To be able to access them, add these entries to your local :file:`/etc/hosts`
  file (or whatever the equivalent is for your operating system):

  .. code-block::
      :caption: excerpt from :file:`/etc/hosts`

      127.0.0.1       admin.byceps.example
      127.0.0.1       api.byceps.example
      127.0.0.1       cozylan.example

- But if you are **installing to a server on the Internet**, substitute above
  hostnames in the configuration with ones that use actual, registered Internet
  domains.


Docker Preparation
==================

Both a :file:`Dockerfile` (to build a Docker image) and a :file:`compose.yml`
(to run containers with Docker Compose) come with BYCEPS.

Create the services (build images, create volumes, etc.). This might take a few
minutes.

.. code-block:: console

    $ docker compose up --no-start


Database
========

Now create and initially populate the relational database structure:

.. code-block:: console

    $ docker compose run --rm byceps-apps uv run byceps initialize-database


Initial User
============

With the tables and the authorization data in place, create the initial user
(which will get all available roles assigned):

.. code-block:: console

    $ docker compose run --rm byceps-apps uv run byceps create-superuser

Enter user account details interactively:

.. code-block:: none

    Screen name: Flynn
    Email address: flynn@flynns-arcade.net
    Password: hunter2

Expected output:

.. code-block:: none

    Creating user "Flynn" ... done.
    Enabling user "Flynn" ... done.
    Assigning 35 roles to user "Flynn" ... done.


Start BYCEPS
============

Now spin up the BYCEPS web applications and the task worker:

.. code-block:: console

    $ docker compose up

The admin frontend should now be available at
http://admin.byceps.example:8080/. Log in with the name of the initial user you
created before and the corresponding password.

The "CozyLAN" party site should be accessible at http://cozylan.example:8080/.
(If you logged in to the admin frontend just before, you might be logged in
already as the same user.)

.. attention:: For security reasons, BYCEPS only sends cookies back after login
   over an HTTPS-secured connection by default.

   It is expected that BYCEPS is run behind a reverse proxy that adds TLS
   termination (e.g. nginx_ or Caddy_; often with a certificate from `Let's
   Encrypt`_).

   To be able to login without HTTPS using above links, you can temporarily
   disable session cookie security: In :file:`compose.yaml` add
   ``SESSION_COOKIE_SECURE: "false"`` on a separate, indented line to the
   section ``x-byceps-base-env``.

.. _nginx: https://nginx.org/
.. _Caddy: https://caddyserver.com/
.. _Let's Encrypt: https://letsencrypt.org/
