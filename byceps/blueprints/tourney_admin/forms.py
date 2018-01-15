"""
byceps.blueprints.tourney_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class TourneyCategoryCreateForm(LocalizedForm):
    title = StringField('Titel', [InputRequired(), Length(max=40)])


class TourneyCategoryUpdateForm(TourneyCategoryCreateForm):
    pass
