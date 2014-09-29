# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple
from datetime import date

from ..orga.models import OrgaFlag
from ..user.models import User, UserDetail


class MonthDay(namedtuple('MonthDay', ['month', 'day'])):

    @classmethod
    def of(cls, date):
        return cls(date.month, date.day)


class Birthday(namedtuple(
        'Birthday',
        ['user', 'date', 'age', 'days_until', 'is_today'])):

    @classmethod
    def of(cls, user, date_of_birth, today):
        month_day_dob = MonthDay.of(date_of_birth)
        month_day_today = MonthDay.of(today)

        age = today.year - date_of_birth.year
        if month_day_dob > month_day_today:
            age -= 1

        days_until = calculate_days_until(date_of_birth, today)

        is_today = (month_day_dob == month_day_today)

        return cls(user, date_of_birth, age, days_until, is_today)


def calculate_days_until(date, today):
    date_this_year = date.replace(year=today.year)
    if date_this_year < today:
        date_this_year = date.replace(year=date_this_year.year + 1)

    delta = date_this_year - today
    return delta.days


def collect_next_orga_birthdays():
    """Return the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = collect_orgas_with_birthdays()
    birthdays = to_birthdays(orgas_with_birthdays)
    return sort_birthdays(birthdays)


def collect_orgas_with_birthdays():
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .all()


def to_birthdays(users):
    """Create birthday objects from users."""
    today = date.today()
    for user in users:
        yield Birthday.of(user, user.detail.date_of_birth, today)


def sort_birthdays(birthdays):
    return sorted(birthdays, key=lambda b: b.days_until)
