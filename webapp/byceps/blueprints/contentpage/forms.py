# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import Form, TextAreaField, TextField


class UpdateForm(Form):
    id = TextField('ID')
    body = TextAreaField('Text')
