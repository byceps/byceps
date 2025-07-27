"""
byceps.services.shop.catalog.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired

from byceps.services.shop.catalog.models import Collection
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import Product
from byceps.services.shop.shop.models import ShopID
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


class ProductAddForm(LocalizedForm):
    product_id = SelectField(
        lazy_gettext('Product'), validators=[InputRequired()]
    )

    def set_product_id_choices(self, collection: Collection, shop_id: ShopID):
        def include_product(product: Product) -> bool:
            return not product.archived and (
                product.id not in collection.product_ids
            )

        products = product_service.get_products_for_shop(shop_id)
        products = [product for product in products if include_product(product)]
        products.sort(key=lambda product: product.item_number)

        def to_label(product):
            return f'{product.item_number} – {product.name}'

        choices = [(str(product.id), to_label(product)) for product in products]
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.product_id.choices = choices
