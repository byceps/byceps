Blueprints
==========

BYCEPS is structured using `Flask's Blueprints`_.

A blueprint acts as a namespace and container for functionality of a
certain topic.

It bundles:

* server-side code (Python, ``*.py``),
* templates (Jinja, ``*.html``),
* and static files, including:

  * front-end styles (CSS, ``*.css``)
  * front-end behaviour (JavaScript, ``*.js``)
  * images (``*.jpeg``, ``*.png``, etc.)

Blueprints should use their own database tables instead of extending or
modifying existing ones.

Generally, blueprints should be self-contained. This should make it easy
to add them to an application, and to disable unwanted ones.

In order to add functionality to BYCEPS, developers are encouraged to
wrap their extensions in a blueprint. This makes it easier to keep the
base system updated without having to worry about conflicts with their
additions. It also makes it easier to distribute their extensions to
other interested BYCEPS users.


Integration
-----------

To fulfill their purpose, blueprints will need to be integrated into
the system one way or another.

A blueprint may build entirely upon the existing system, and just
require a few URL references to be inserted in the navigation or some
templates of the base system.

If a blueprint should react on certain events, it can connect to the
available :doc:`signals <../concepts/signals>`.


.. _Flask's Blueprints: https://flask.palletsprojects.com/en/1.1.x/blueprints/
