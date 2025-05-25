"""
byceps.services.shop.catalog.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class _CatalogBaseForm(LocalizedForm):
    title = StringField(lazy_gettext('Title'), validators=[InputRequired()])


class CatalogCreateForm(_CatalogBaseForm):
    pass


class CatalogUpdateForm(_CatalogBaseForm):
    pass


class _CollectionBaseForm(LocalizedForm):
    title = StringField(lazy_gettext('Title'), validators=[InputRequired()])


class CollectionCreateForm(_CollectionBaseForm):
    pass


class CollectionUpdateForm(_CollectionBaseForm):
    pass
