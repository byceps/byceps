Scopes
======

BYCEPS distinguishes three scopes:

* :ref:`global <scope-global>`
* :ref:`brand <scope-brand>`
* :ref:`party <scope-party>`

.. graph:: unnamed

   subgraph clusterGlobal {
     label = "global"

     subgraph clusterBrand {
       label = "brand"

       node [shape=box] party;
     }
   }

Each entity belongs to exactly one of these scopes.


.. _scope-global:

Global
------

The global scope is the outermost one.

Entities that belong to the global scope include users and
:ref:`brands <scope-brand>`.


.. _scope-brand:

Brand
-----

A brand is the identity of a series of parties.

Each brand is part of the :ref:`global <scope-global>` scope.

Entities that belong to the brand scope include news posts, boards, and,
of course, :ref:`parties <scope-party>`.


.. _scope-party:

Party
-----

The party scope is the innermost one.

Each party belongs to a :ref:`brand <scope-brand>`.

Entities that belong to the party scope include seating areas and
tickets.
