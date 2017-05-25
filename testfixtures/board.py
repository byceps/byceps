"""
testfixtures.board
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import category_service, posting_service, \
    topic_service

from .brand import create_brand


def create_category(*, brand=None, number=1, slug=None, title=None,
                    description=None):
    if brand is None:
        brand = create_brand()

    if slug is None:
        slug = 'category-{}'.format(number)

    if title is None:
        title = 'Kategorie {}'.format(number)

    if description is None:
        description = 'Hier geht es um Kategorie {}'.format(number)

    return category_service.create_category(brand, slug, title, description)


def create_topic(category, creator_id, *, number=1, title=None, body=None):
    if title is None:
        title = 'Thema {}'.format(number)

    if body is None:
        body = 'Inhalt von Thema {}'.format(number)

    return topic_service.create_topic(category, creator_id, title, body)


def create_posting(topic, creator_id, *, number=1, body=None):
    if body is None:
        body = 'Inhalt von Beitrag {}.'.format(number)

    return posting_service.create_posting(topic, creator_id, body)
