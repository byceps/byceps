# -*- coding: utf-8 -*-

"""
byceps.util.datetime.range
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple


class DateTimeRange(namedtuple('DateTimeRange', ['start', 'end'])):
    """A date/time range with an inclusive start and an exclusive end."""

    __slots__ = ()

    def contains(self, datetime):
        return self.start <= datetime < self.end

    def __repr__(self):
        return '[{0.start}..{0.end})'.format(self)
