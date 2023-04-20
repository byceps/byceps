"""
byceps.blueprints.admin.orga_presence.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask_babel import gettext, lazy_gettext, to_user_timezone, to_utc
from wtforms import DateField, TimeField
from wtforms.validators import InputRequired

from byceps.util.datetime.range import DateTimeRange
from byceps.util.l10n import LocalizedForm


def build_presence_create_form(dt_range: DateTimeRange):

    dt_range = dt_range._replace(
        start=to_user_timezone(dt_range.start).replace(tzinfo=None),
        end=to_user_timezone(dt_range.end).replace(tzinfo=None),
    )

    class CreateForm(LocalizedForm):
        starts_on = DateField(
            lazy_gettext('Start date'),
            default=dt_range.start.date,
            validators=[InputRequired()],
        )
        starts_at = TimeField(
            lazy_gettext('Start time'),
            default=dt_range.start.time,
            validators=[InputRequired()],
        )
        ends_on = DateField(
            lazy_gettext('End date'),
            default=dt_range.end.date,
            validators=[InputRequired()],
        )
        ends_at = TimeField(
            lazy_gettext('End time'),
            default=dt_range.end.time,
            validators=[InputRequired()],
        )

        def validate(self) -> bool:
            if not super().validate():
                return False

            valid = True

            starts_at = to_utc(
                datetime.combine(self.starts_on.data, self.starts_at.data)
            )
            ends_at = to_utc(
                datetime.combine(self.ends_on.data, self.ends_at.data)
            )

            for dt, field_date, field_time in [
                (starts_at, self.starts_on, self.starts_at),
                (ends_at, self.ends_on, self.ends_at),
            ]:
                if dt not in dt_range:
                    for field in field_date, field_time:
                        field.errors.append(
                            gettext('Value must be in valid range.')
                        )
                    valid = False

            if starts_at >= ends_at:
                self.form_errors.append(
                    gettext('Start value must be before end value.')
                )
                valid = False

            return valid

    return CreateForm
