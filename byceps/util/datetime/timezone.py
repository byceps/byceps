"""
byceps.util.datetime.timezone
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timezone helpers

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import current_app
import pendulum



def local_tz_to_utc(dt: datetime):
    """Convert date/time object from configured default local time to UTC."""
    tz_str = get_timezone_string()

    return (pendulum.instance(dt)
        .set(tz=tz_str)
        .in_tz(pendulum.UTC)
        # Keep SQLAlchemy from converting it to another zone.
        .replace(tzinfo=None))


def utc_to_local_tz(dt: datetime) -> datetime:
    """Convert naive date/time object from UTC to configured time zone."""
    tz_str = get_timezone_string()
    return pendulum.instance(dt).in_tz(tz_str)


def get_timezone_string() -> str:
    """Return the configured default timezone as a string."""
    return current_app.config['TIMEZONE']
