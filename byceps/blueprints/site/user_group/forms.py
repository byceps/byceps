"""
byceps.blueprints.site.user_group.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField, TextAreaField

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField('Titel')
    description = TextAreaField('Beschreibung')
