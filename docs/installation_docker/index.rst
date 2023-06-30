*****************************
Installation (Docker Compose)
*****************************

As an alternative to :doc:`installing directly on a system
</installation/index>`, BYCEPS can be run from Docker_ containers,
orchestrated by `Docker compose`_.

.. _Docker: https://www.docker.com/
.. _Docker Compose: https://docs.docker.com/compose/

First, create the services (build images, create volumes, etc.). This
might take a few minutes.

.. code-block:: sh

    $ docker-compose up --no-start

Then generate a *secret key* and put it in a file Docker Compose is
configured to pick up as a secret_:

.. _secret: https://docs.docker.com/compose/use-secrets/

.. code-block:: sh

    $ docker-compose run --rm byceps-admin byceps generate-secret-key > ./secret_key.txt

Now create and initially populate the relational database structure:

.. code-block:: sh

    $ docker-compose run --rm byceps-admin byceps initialize-database

Optionally, insert demonstration data to get a feel for how BYCEPS set
up with a party, a party site, etc. looks like:

.. code-block:: sh

    $ docker-compose run --rm byceps-admin byceps create-demo-data

To spin up the application:

.. code-block:: sh

    $ docker-compose up

The admin frontend should now be available at http://localhost:8081/.
Log in with user ``DemoAdmin`` and password ``demodemo``.

The "CozyLAN" party site should be accessible at http://localhost:8082/.
(If you logged in to the admin frontend just before, you might be logged
in already as user ``DemoAdmin``.)
