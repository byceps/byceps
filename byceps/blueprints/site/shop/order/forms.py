"""
byceps.blueprints.site.shop.order.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from moneyed import EUR
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Orderer
from byceps.services.user.models.user import User
from byceps.util.l10n import LocalizedForm


class OrderForm(LocalizedForm):
    company = StringField(lazy_gettext('Company'), validators=[Optional()])
    first_name = StringField(
        lazy_gettext('First name'), validators=[Length(min=2)]
    )
    last_name = StringField(
        lazy_gettext('Last name'), validators=[Length(min=2)]
    )
    country = StringField(
        lazy_gettext('Country'), validators=[Length(min=2, max=60)]
    )
    zip_code = StringField(
        lazy_gettext('Zip code'),
        validators=[Length(min=4, max=5)],  # DE: 5 digits, AT/CH: 4 digits
    )
    city = StringField(lazy_gettext('City'), validators=[Length(min=2)])
    street = StringField(lazy_gettext('Street'), validators=[Length(min=2)])

    def get_orderer(self, user: User) -> Orderer:
        return Orderer(
            user=user,
            company=(self.company.data or '').strip(),
            first_name=self.first_name.data.strip(),
            last_name=self.last_name.data.strip(),
            country=self.country.data.strip(),
            zip_code=self.zip_code.data.strip(),
            city=self.city.data.strip(),
            street=self.street.data.strip(),
        )


def assemble_products_order_form(product_compilation):
    """Dynamically extend the order form with one field per product."""

    class ProductsOrderForm(OrderForm):
        def get_field_for_product(self, product):
            name = _generate_field_name(product)
            return getattr(self, name)

        def get_cart(self, product_compilation):
            cart = Cart(EUR)
            for product, quantity in self.get_cart_items(product_compilation):
                cart.add_item(product, quantity)
            return cart

        def get_cart_items(self, product_compilation):
            for item in product_compilation:
                quantity = self.get_field_for_product(item.product).data
                if quantity > 0:
                    yield item.product, quantity

    validators = [InputRequired()]
    for item in product_compilation:
        field_name = _generate_field_name(item.product)
        choices = _create_choices(item.product)
        field = SelectField(
            lazy_gettext('Quantity'), validators, coerce=int, choices=choices
        )
        setattr(ProductsOrderForm, field_name, field)

    return ProductsOrderForm


def _generate_field_name(product):
    return f'product_{product.id}'


def _create_choices(product):
    max_orderable_quantity = _get_max_orderable_quantity(product)
    quantities = list(range(max_orderable_quantity + 1))
    return [(quantity, str(quantity)) for quantity in quantities]


def _get_max_orderable_quantity(product):
    return min(product.quantity, product.max_quantity_per_order)
