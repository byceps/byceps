"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Optional

from byceps.services.language import language_service
from byceps.services.snippet.dbmodels import DbSnippet
from byceps.util.forms import MultiCheckboxField
from byceps.util.l10n import LocalizedForm


class CopySnippetsForm(LocalizedForm):
    source_snippet_ids = MultiCheckboxField(
        lazy_gettext('Snippets'), validators=[Optional()]
    )

    def set_source_snippet_id_choices(self, snippets: Sequence[DbSnippet]):
        snippets = list(snippets)
        snippets.sort(key=lambda snippet: (snippet.name, snippet.language_code))

        self.source_snippet_ids.choices = [
            (str(snippet.id), f'{snippet.name} ({snippet.language_code})')
            for snippet in snippets
        ]


class CreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    language_code = SelectField(
        lazy_gettext('Language code'), [InputRequired()]
    )
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])

    def set_language_code_choices(self):
        languages = language_service.get_languages()
        choices = [(language.code, language.code) for language in languages]
        choices.sort()
        self.language_code.choices = choices


class UpdateForm(CreateForm):
    pass
