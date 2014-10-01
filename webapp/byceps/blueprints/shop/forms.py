# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import DateField, StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class OrderForm(LocalizedForm):
    first_names = StringField('Vorname(n)', validators=[Length(min=2)])
    last_name = StringField('Nachname', validators=[Length(min=2)])
    date_of_birth = DateField('Geburtsdatum', format='%d.%m.%Y', validators=[InputRequired()])
    zip_code = StringField('PLZ', validators=[Length(min=5, max=5)])
    city = StringField('Stadt', validators=[Length(min=2)])
    street = StringField('Straße', validators=[Length(min=2)])
