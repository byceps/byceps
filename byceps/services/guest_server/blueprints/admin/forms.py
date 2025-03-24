"""
byceps.services.guest_server.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import gettext, lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import (
    InputRequired,
    IPAddress,
    Length,
    Optional,
    Regexp,
)

from byceps.util.forms import UserScreenNameField
from byceps.util.l10n import LocalizedForm


class SettingUpdateForm(LocalizedForm):
    netmask = StringField(
        lazy_gettext('Netmask'), validators=[Optional(), IPAddress(ipv6=True)]
    )
    gateway = StringField(
        lazy_gettext('Gateway'), validators=[Optional(), IPAddress(ipv6=True)]
    )
    dns_server1 = StringField(
        lazy_gettext('DNS server') + ' 1',
        validators=[Optional(), IPAddress(ipv6=True)],
    )
    dns_server2 = StringField(
        lazy_gettext('DNS server') + ' 2',
        validators=[Optional(), IPAddress(ipv6=True)],
    )
    domain = StringField(lazy_gettext('Domain'), validators=[Optional()])


HOSTNAME_REGEX = re.compile('^[A-Za-z][A-Za-z0-9-]+$')


class ServerRegisterForm(LocalizedForm):
    owner = UserScreenNameField(lazy_gettext('Owner'), [InputRequired()])
    description = StringField(
        lazy_gettext('Description'),
        validators=[InputRequired(), Length(max=100)],
    )
    ip_address = StringField(
        lazy_gettext('IP address'),
        validators=[Optional(), IPAddress(ipv6=True)],
    )
    hostname = StringField(
        lazy_gettext('Hostname'),
        validators=[
            InputRequired(),
            Length(min=2, max=20),
            Regexp(HOSTNAME_REGEX),
        ],
    )
    netmask = StringField(
        lazy_gettext('Netmask'), validators=[Optional(), IPAddress(ipv6=True)]
    )
    gateway = StringField(
        lazy_gettext('Gateway'), validators=[Optional(), IPAddress(ipv6=True)]
    )
    notes_admin = TextAreaField(
        lazy_gettext('Notes by admin'),
        validators=[Optional(), Length(max=1000)],
    )


class ServerUpdateForm(LocalizedForm):
    notes_admin = TextAreaField(
        lazy_gettext('Notes by admin'), validators=[Optional()]
    )


class _AddressBaseForm(LocalizedForm):
    ip_address = StringField(
        lazy_gettext('IP address'),
        validators=[Optional(), IPAddress(ipv6=True)],
    )
    hostname = StringField(
        lazy_gettext('Hostname'),
        validators=[Optional(), Length(max=20), Regexp(HOSTNAME_REGEX)],
    )
    netmask = StringField(
        lazy_gettext('Netmask'), validators=[Optional(), IPAddress(ipv6=True)]
    )
    gateway = StringField(
        lazy_gettext('Gateway'), validators=[Optional(), IPAddress(ipv6=True)]
    )


class AddressCreateForm(_AddressBaseForm):
    def validate(self) -> bool:
        if not super().validate():
            return False

        if not self.ip_address.data and not self.hostname.data.strip():
            self.form_errors.append(
                gettext('Provide at least an IP address or a hostname.')
            )
            return False

        return True


class AddressUpdateForm(_AddressBaseForm):
    pass
