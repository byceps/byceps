# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Posting, Topic


def create_topic(category, creator, title, body):
    """Create a topic with an initial posting in that category."""
    topic = Topic(category, creator, title)
    posting = Posting(topic, creator, body)

    db.session.add(topic)
    db.session.add(posting)
    db.session.commit()

    topic.aggregate()

    return topic


def create_posting(topic, creator, body):
    """Create a posting in that topic."""
    posting = Posting(topic, creator, body)
    db.session.add(posting)
    db.session.commit()

    topic.aggregate()

    return posting
