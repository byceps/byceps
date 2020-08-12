Signals
=======

BYCEPS makes use of signals (based on the Blinker_ package) to provide
hooks for specific events.

For example, a signal is emitted every time

* a user account is created
* a topic in the board is created
* an order is placed in the shop

Besides representing the information *that* something happened, signals
can (and usually do) contain relevant objects as well.

To receive signals, handlers can be registered for those they are
interested in.

Some specific knowledge is necessary to attach code to a specific
signal and access its payload, though.

* to import it: the module and name of the signal

* to handle it: the types of the objects it contains, and the keyword
  argument names they can be accessed with


Example
-------

As a simple example for learning purposes, here is the code to print a
message to STDOUT (visible when manually starting the application from
the command line, e.g. for development and debugging).

.. code-block:: python

    from byceps.events.board import BoardTopicCreated
    from byceps.signals.board import topic_created

    @topic_created.connect
    def celebrate_created_topic(sender, *, event: BoardTopicCreated = None) -> None:
        print(f'A topic titled has been created: {event.url}')

More useful reactions include:

* announcing selected events via email, on IRC, or on social media sites
* creating/assigning a party ticket once the corresponding order has been paid
* running spam detection on new board topics and postings

.. _Blinker: https://pythonhosted.org/blinker/
