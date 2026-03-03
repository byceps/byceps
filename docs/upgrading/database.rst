Database Migrations
===================

Adjustments and new features sometimes require changes to the database
structure.

Those changes usually come in two forms:

1. DDL statements to change the structure of one or more tables, sometimes
   accompanied by SQL statements that add or adjust data.

   Use an SQL client (like PostgreSQL's `psql` command-line utility) connected
   to the BYCEPS database to execute those statements.

2. Calling the :ref:`create-database-tables <Create Database Tables>` command
   again which will then create new tables as necessary.

.. tip:: Consider updating BYCEPS regularly to keep the number of database
   migrations that need to be applied low.

To learn which migrations need to be applied, follow the channel "db-changelog"
on the BYCEPS Discord server.
