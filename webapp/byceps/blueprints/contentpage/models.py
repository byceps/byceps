# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple
from operator import itemgetter

from ...database import db
from ...util.instances import ReprBuilder

from .models import User


class ContentPage(db.Model):
    """A content page."""
    __tablename__ = 'content_pages'

    id = db.Column(db.Unicode(40), primary_key=True)
    url = db.Column(db.Unicode(40), unique=True)
    body = db.Column(db.UnicodeText)

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id') \
            .add('url') \
            .build()



ContentPageReference = namedtuple(
    'ContentPageReference', 'id view_url update_url')


def collect_all_content_page_ids():
    content_pages = db.session.query(ContentPage.id).distinct().all()
    return frozenset(map(itemgetter(0), content_pages))
