# -*- coding: utf-8 -*-

"""
byceps.util.instances
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""


class ReprBuilder(object):
    """An instance representation builder."""

    def __init__(self, instance):
        self.instance = instance
        self.attribute_names = []

    def add(self, attribute_name):
        self.attribute_names.append(attribute_name)
        return self

    def build(self):
        class_name = type(self.instance).__name__
        attributes = ', '.join(self._get_attributes())
        return '<{}({})>'.format(class_name, attributes)

    def _get_attributes(self):
        for name in self.attribute_names:
            value = getattr(self.instance, name)
            yield '{}={}'.format(name, value)
