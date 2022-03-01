"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class FragmentCreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])


class FragmentUpdateForm(FragmentCreateForm):
    pass


class DocumentCreateForm(FragmentCreateForm):
    title = StringField(lazy_gettext('Title'), [InputRequired()])
    head = TextAreaField(lazy_gettext('Page header'))
    image_url_path = StringField(lazy_gettext('Image URL path'))


class DocumentUpdateForm(DocumentCreateForm):
    pass
