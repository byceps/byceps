Scopes
======

BYCEPS distinguishes four scopes:

* :ref:`global <scope-global>`
* :ref:`brand <scope-brand>`
* :ref:`party <scope-party>`
* :ref:`site <scope-site>`

.. graph:: unnamed

   color=lightgray
   fillcolor=white
   labeljust="l"
   style=filled

   subgraph cluster_global {
     label="global"

     subgraph cluster_brand {
       label="brand"

       subgraph cluster_party {
         label="party"

         subgraph cluster_party {
           label="site"

           node [color=transparent] "";
         }
       }
     }
   }

Each entity belongs to exactly one of these scopes.


.. _scope-global:

Global
------

The global scope is the outermost one.

Entities that belong to the global scope include users, roles,
permissions, user badges, :ref:`brands <scope-brand>`, and optionally
snippets.


.. _scope-brand:

Brand
-----

A brand is the identity of a series of parties.

Each brand is part of the :ref:`global <scope-global>` scope.

Entities that belong to the brand scope include orga flags, terms of
service versions, news channels, boards, :ref:`parties <scope-party>`,
and optionally snippets.


.. _scope-party:

Party
-----

The party scope is for entities that belong to a single party (and are
not better situated in the :ref:`site scope <scope-site>`).

Each party belongs to a :ref:`brand <scope-brand>`.

Entities that belong to the party scope include orga teams, shops,
tickets, seating areas, and :ref:`sites <scope-site>`.


.. _scope-site:

Site
----

The site scope is the innermost one.

Each site belongs to a :ref:`party <scope-party>`.

Entities that *can* belong to the site scope include snippets.
