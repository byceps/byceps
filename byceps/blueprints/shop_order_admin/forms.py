# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_order_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CancelForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=200)])
