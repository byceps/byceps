"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID


SubjectID = NewType('SubjectID', UUID)
