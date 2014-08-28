# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import TextAreaField, TextField
from wtforms.validators import Required

from ...util.l10n import LocalizedForm


class PostingCreateForm(LocalizedForm):
    body = TextAreaField('Text', validators=[Required()])


class TopicCreateForm(PostingCreateForm):
    title = TextField('Titel', validators=[Required()])
