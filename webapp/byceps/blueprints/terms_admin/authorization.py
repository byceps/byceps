# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


TermsPermission = create_permission_enum('terms', [
    'list',
    'create',
])
