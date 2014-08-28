# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


TermsPermission = create_permission_enum('terms', [
    'list',
    'create',
])
