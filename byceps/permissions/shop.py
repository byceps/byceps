"""
byceps.permissions.shop_shop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'shop',
    [
        ('create', lazy_gettext('Create shops')),
        ('update', lazy_gettext('Edit shops')),
        ('view', lazy_gettext('View shops')),
    ],
)


register_permissions(
    'shop_article',
    [
        ('create', lazy_gettext('Create shop articles')),
        ('update', lazy_gettext('Edit shop articles')),
        ('view', lazy_gettext('View shop articles')),
    ],
)


register_permissions(
    'shop_order',
    [
        ('cancel', lazy_gettext('Cancel shop orders')),
        ('mark_as_paid', lazy_gettext('Mark shop orders as paid')),
        ('update', lazy_gettext('Edit shop orders')),
        ('view', lazy_gettext('View shop orders')),
    ],
)
