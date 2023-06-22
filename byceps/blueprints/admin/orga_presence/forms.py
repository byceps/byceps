"""
byceps.blueprints.admin.orga_presence.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask_babel import gettext, lazy_gettext, to_user_timezone, to_utc
from wtforms import DateTimeLocalField
from wtforms.validators import InputRequired

from byceps.util.datetime.range import DateTimeRange
from byceps.util.l10n import LocalizedForm


DATE_TIME_LOCAL_FIELD_FORMAT = '%Y-%m-%dT%H:%M'


def build_presence_create_form(valid_range_utc: DateTimeRange):
    valid_range_local = dataclasses.replace(
        valid_range_utc,
        start=to_user_timezone(valid_range_utc.start).replace(tzinfo=None),
        end=to_user_timezone(valid_range_utc.end).replace(tzinfo=None),
    )

    class CreateForm(LocalizedForm):
        starts_at = DateTimeLocalField(
            lazy_gettext('Start'),
            default=valid_range_local.start,
            validators=[InputRequired()],
            format=DATE_TIME_LOCAL_FIELD_FORMAT,
        )
        ends_at = DateTimeLocalField(
            lazy_gettext('End'),
            default=valid_range_local.end,
            validators=[InputRequired()],
            format=DATE_TIME_LOCAL_FIELD_FORMAT,
        )

        def validate(self) -> bool:
            if not super().validate():
                return False

            valid = True

            starts_at = to_utc(self.starts_at.data)
            ends_at = to_utc(self.ends_at.data)

            def append_date_time_error(field):
                field.errors.append(gettext('Value must be in valid range.'))

            if not (valid_range_utc.start <= starts_at < valid_range_utc.end):
                append_date_time_error(self.starts_at)
                valid = False

            # As the presence end timestamp is exclusive, it may match
            # the date range's end, which is exclusive, too.
            if not (valid_range_utc.start <= ends_at <= valid_range_utc.end):
                append_date_time_error(self.ends_at)
                valid = False

            if starts_at >= ends_at:
                self.form_errors.append(
                    gettext('Start value must be before end value.')
                )
                valid = False

            return valid

    return CreateForm
