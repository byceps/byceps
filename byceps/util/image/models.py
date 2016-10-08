# -*- coding: utf-8 -*-

"""
byceps.util.image.models
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from enum import Enum


Dimensions = namedtuple('Dimensions', ['width', 'height'])


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png'])
