"""
byceps.services.newsletter.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.user.models import UserID

from .models import ListID, SubscriptionState


class DbList(db.Model):
    """A newsletter list users can subscribe to."""

    __tablename__ = 'newsletter_lists'

    id: Mapped[ListID] = mapped_column(db.UnicodeText, primary_key=True)
    title: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, list_id: ListID, title: str) -> None:
        self.id = list_id
        self.title = title


class DbSubscription(db.Model):
    """A user's subscription to a list."""

    __tablename__ = 'newsletter_subscriptions'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    list_id: Mapped[ListID] = mapped_column(
        db.UnicodeText, db.ForeignKey('newsletter_lists.id'), primary_key=True
    )


class DbSubscriptionUpdate(db.Model):
    """A user's declaration on wanting/not wanting to receive
    newsletters from this list.
    """

    __tablename__ = 'newsletter_subscription_updates'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    list_id: Mapped[ListID] = mapped_column(
        db.UnicodeText, db.ForeignKey('newsletter_lists.id'), primary_key=True
    )
    expressed_at: Mapped[datetime] = mapped_column(primary_key=True)
    _state: Mapped[str] = mapped_column('state', db.UnicodeText)

    def __init__(
        self,
        user_id: UserID,
        list_id: ListID,
        expressed_at: datetime,
        state: SubscriptionState,
    ) -> None:
        self.user_id = user_id
        self.list_id = list_id
        self.expressed_at = expressed_at
        self.state = state

    @hybrid_property
    def state(self) -> SubscriptionState:
        return SubscriptionState[self._state]

    @state.setter
    def state(self, state: SubscriptionState) -> None:
        self._state = state.name
