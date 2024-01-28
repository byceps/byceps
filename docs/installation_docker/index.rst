*****************************
Installation (Docker Compose)
*****************************

As an alternative to :doc:`installing directly on a system
</installation/index>`, BYCEPS can be run from Docker_ containers,
orchestrated by `Docker compose`_.

.. important:: This guide assumes you are using Docker Compose V2. If
   you are still using V1, replace ``docker compose`` with
   ``docker-compose`` before running commands that include it.

Since there is no official Docker image for BYCEPS at this point, you
have to build one yourself.

.. _Docker: https://www.docker.com/
.. _Docker Compose: https://docs.docker.com/compose/

First, clone BYCEPS' Git repository to your machine:

.. code-block:: sh

    $ git clone https://github.com/byceps/byceps.git

A new directory, ``byceps``, should have been created. ``cd`` into it.

Both a ``Dockerfile`` (to build a Docker image) and a ``compose.yml``
(to run containers with Docker Compose) come with BYCEPS.

Create the services (build images, create volumes, etc.). This might
take a few minutes.

.. code-block:: sh

    $ docker compose up --no-start

Then generate a *secret key* and put it in a file Docker Compose is
configured to pick up as a secret_:

.. _secret: https://docs.docker.com/compose/use-secrets/

.. code-block:: sh

    $ docker compose run --rm byceps-admin byceps generate-secret-key > ./secret_key.txt

Now create and initially populate the relational database structure:

.. code-block:: sh

    $ docker compose run --rm byceps-admin byceps initialize-database

With the tables and the authorization data in place, create the initial
user (which will get all available roles assigned):

.. code-block:: sh

    $ docker compose run --rm byceps-admin byceps create-superuser
    Screen name: Flynn
    Email address: flynn@flynns-arcade.net
    Password:
    Creating user "Flynn" ... done.
    Enabling user "Flynn" ... done.
    Assigning 35 roles to user "Flynn" ... done.

To spin up the application:

.. code-block:: sh

    $ docker compose up

The admin frontend should now be available at http://localhost:8081/.
Log in with the name of the initial user you created before and the
corresponding password.

The "CozyLAN" party site should be accessible at http://localhost:8082/.
(If you logged in to the admin frontend just before, you might be logged
in already as the same user.)

.. attention:: For security reasons, BYCEPS only sends cookies back
   after login over an HTTPS-secured connection by default.

   It is expected that BYCEPS is run behind a reverse proxy that adds
   TLS termination (e.g. nginx_ or Caddy_; often with a certificate from
   `Let's Encrypt`_).

   To be able to login without HTTPS using above links, you can
   temporarily disable session cookie security by setting
   :py:data:`SESSION_COOKIE_SECURE` to false: In ``compose.yaml`` add
   ``SESSION_COOKIE_SECURE: false`` on a separate, indented line to the
   section ``x-byceps-base-env``.

.. _nginx: https://nginx.org/
.. _Caddy: https://caddyserver.com/
.. _Let's Encrypt: https://letsencrypt.org/
