"""
byceps.blueprints.admin.terms.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


TermsPermission = create_permission_enum('terms', [
    'create',
    'view',
])
