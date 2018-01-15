"""
testfixtures.news
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.news.models import CurrentVersionAssociation, Item, \
    ItemVersion


def create_item(brand_id, *, slug='a-news-item-about-something-nice'):
    return Item(brand_id, slug)


def create_item_version(item, creator_id, *, created_at=None, title='', body='',
                        image_url_path=None):
    version = ItemVersion(item, creator_id, title, body)
    version.created_at = created_at
    version.image_url_path = image_url_path
    return version


def create_current_version_association(item, version):
    return CurrentVersionAssociation(item, version)
