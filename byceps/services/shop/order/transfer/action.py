"""
byceps.services.shop.order.transfer.action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any, Dict
from uuid import UUID

from ...article.transfer.models import ArticleID

from .order import PaymentState


ActionParameters = Dict[str, Any]


@dataclass(frozen=True)
class Action:
    id: UUID
    article_id: ArticleID
    payment_state: PaymentState
    procedure_name: str
    parameters: ActionParameters
