"""
byceps.services.guest_server.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask import g
from flask_babel import lazy_gettext
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import (
    InputRequired,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from byceps.services.guest_server import guest_server_service
from byceps.util.l10n import LocalizedForm


MAXIMUM_ADDRESS_QUANTITY_PER_SERVER = 5

HOSTNAME_REGEX = re.compile('^[A-Za-z][A-Za-z0-9-]+$')


def generate_address_indexes(quantity: int) -> list[int]:
    if quantity > MAXIMUM_ADDRESS_QUANTITY_PER_SERVER:
        quantity = MAXIMUM_ADDRESS_QUANTITY_PER_SERVER

    return list(range(1, quantity + 1))


def generate_hostname_field_name(address_index: int) -> str:
    return f'hostname{address_index}'


def validate_hostname(form, field):
    hostname = field.data.strip()

    if guest_server_service.is_hostname_registered(g.party.id, hostname):
        raise ValidationError(
            lazy_gettext('This value is not available. Please choose another.')
        )


class AddressQuantityForRegistrationForm(LocalizedForm):
    address_quantity = SelectField(
        lazy_gettext('Quantity of addresses needed'),
        validators=[InputRequired()],
        coerce=int,
        choices=[
            (index, str(index))
            for index in generate_address_indexes(
                MAXIMUM_ADDRESS_QUANTITY_PER_SERVER
            )
        ],
    )


class _RegisterFormBase(LocalizedForm):
    description = StringField(
        lazy_gettext('Description'),
        validators=[InputRequired(), Length(max=100)],
    )
    notes = TextAreaField(
        lazy_gettext('Notes'), validators=[Optional(), Length(max=1000)]
    )


def generate_register_form_with_variable_address_quantity(
    address_quantity: int,
):
    """Dynamically generate a form for guest server registration with a
    variable number of hostname fields.
    """

    class VariableAddressQuantityRegisterForm(_RegisterFormBase):
        pass

    validators = [
        InputRequired(),
        Length(min=2, max=20),
        Regexp(HOSTNAME_REGEX),
        validate_hostname,
    ]

    for address_index in generate_address_indexes(address_quantity):
        field_name = generate_hostname_field_name(address_index)
        label = lazy_gettext('Hostname') + f' {address_index}'
        field = StringField(label, validators)
        setattr(VariableAddressQuantityRegisterForm, field_name, field)

    return VariableAddressQuantityRegisterForm
