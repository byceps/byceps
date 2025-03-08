"""
byceps.services.shop.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'shop',
    [
        ('create', lazy_gettext('Create shops')),
        ('update', lazy_gettext('Edit shops')),
        ('view', lazy_gettext('View shops')),
    ],
)


register_permissions(
    'shop_product',
    [
        ('administrate', lazy_gettext('Administrate shop products')),
        ('view', lazy_gettext('View shop products')),
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
