Seating
=======

BYCEPS' seating model was designed to be flexible enough to fit both
:ref:`small parties <seating-example-small>` (say, less than a hundred
seats in a single hall) as well as :ref:`big ones <seating-example-big>`
(like Northern LAN Convention – NorthCon_ – with around 3.500 seats).

.. _NorthCon: https://www.northcon.de/


Structure
---------

.. digraph:: unnamed

   rankdir=BT

   subgraph cluster_seating {
     color=lightgray
     fillcolor=lightgray
     label="Seating"
     labeljust="l"
     node [color=white, style=filled]
     rankdir=LR
     style=filled

     Seat -> {Area Category}
   }

   node [color=lightgray, style=filled]

   Area -> Party
   Category -> Party

Each seat references these two entities:

* An **area** represents the physical location of a group of seats.

* A **category** is meant to separate seats in different price ranges
  from each another.

  Since a ticket is bound to a category, a user with a ticket from
  category X cannot reserve a seat that belongs to category Y.

Each area and category belongs to a specific party since each seating
setup often is party-specific (even if multiple parties are held in the
same location).


.. _seating-example-small:

Example: Small Party
--------------------

A small party may take place in a single room or hall, and no
distinction is made between the seats in it. Thus, a single area as well
as a single category are sufficient, so every seat belongs to the same
area and the same category.

.. digraph:: unnamed

   color=lightgray
   fillcolor=lightgray
   labeljust="l"
   node [color=white, style=filled]
   rankdir=LR
   style=filled

   subgraph cluster_categories {
     label="Categories"
     node [color=lightgray]
     style=""

     category_regular [label="Regular"]
   }

   subgraph cluster_areas {
     label="Areas"

     subgraph cluster_area1 {
       label="Area 1"

       seats_area1_regular [label="80 ×\nRegular"]

       seats_area1_regular -> category_regular
     }

     style=""
   }


.. _seating-example-big:

Example: Big Party
------------------

This is a setup for a party that is held in multiple halls and which
offers seats in multiple price (and feature) ranges.

.. digraph:: unnamed

   color=lightgray
   fillcolor=lightgray
   labeljust="l"
   node [color=white, style=filled]
   style=filled

   subgraph cluster_categories {
     label="Categories"
     labelloc="b"
     node [color=lightgray]
     style=""

     category_vip [label="VIP"]
     category_premium [label="Premium"]
     category_regular [label="Regular"]
   }

   subgraph cluster_areas {
     label="Areas"

     subgraph cluster_area1 {
       label="Area 1"

       seats_area1_regular [label="1200 ×\nRegular"]

       seats_area1_regular -> category_regular
     }

     subgraph cluster_area2 {
       label="Area 2"

       seats_area2_regular [label="400 ×\nRegular"]
       seats_area2_premium [label="150 ×\nPremium"]

       seats_area2_regular -> category_regular
       seats_area2_premium -> category_premium
     }

     subgraph cluster_area3 {
       label="Area 3"

       seats_area3_regular [label="600 ×\nRegular"]
       seats_area3_premium [label="250 ×\nPremium"]
       seats_area3_vip [label="10 ×\nVIP"]

       seats_area3_regular -> category_regular
       seats_area3_premium -> category_premium
       seats_area3_vip -> category_vip
     }

     style=""
   }
