"""
byceps.services.snippet.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import NewType
from uuid import UUID


SnippetID = NewType('SnippetID', UUID)


SnippetType = Enum('SnippetType', ['document', 'fragment'])


SnippetVersionID = NewType('SnippetVersionID', UUID)


MountpointID = NewType('MountpointID', UUID)
