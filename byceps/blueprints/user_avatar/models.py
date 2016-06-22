# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_avatar.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from pathlib import Path

from flask import current_app, url_for


class Avatar(namedtuple('Avatar', ['user_id', 'created_at', 'image_type'])):
    """A user's avatar image."""

    @property
    def filename(self):
        timestamp = int(self.created_at.timestamp())
        name_without_suffix = '{}_{:d}'.format(self.user_id, timestamp)
        suffix = '.' + self.image_type.name
        return Path(name_without_suffix).with_suffix(suffix)

    @property
    def path(self):
        path = current_app.config['PATH_USER_AVATAR_IMAGES']
        return path / self.filename

    @property
    def url(self):
        path = 'users/avatars/{}'.format(self.filename)
        return url_for('global_file', filename=path)
