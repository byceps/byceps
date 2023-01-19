"""
byceps.services.global_setting.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GlobalSetting:
    name: str
    value: str
