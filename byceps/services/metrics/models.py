"""
byceps.services.metrics.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List

from attr import attrib, attrs


@attrs(frozen=True, slots=True)
class Label:
    name = attrib(type=str)
    value = attrib(type=str)

    def serialize(self) -> str:
        escaped_value = _escape_label_value(self.value)
        return '{}="{}"'.format(self.name, escaped_value)


def _escape_label_value(value: str) -> str:
    def escape(char):
        if char == '\\':
            return r'\\'
        elif char == '"':
            return r'\"'
        elif char == '\n':
            return r'\n'
        else:
            return char

    return ''.join(map(escape, value))


@attrs(frozen=True, slots=True)
class Metric:
    name = attrib(type=str)
    value = attrib(type=float)
    labels = attrib(factory=dict, kw_only=True, type=List[Label])

    def serialize(self) -> str:
        labels_str = ''
        if self.labels:
            labels_str = '{' \
                + ', '.join(label.serialize() for label in self.labels) \
                + '}'

        return '{}{} {}'.format(self.name, labels_str, self.value)
