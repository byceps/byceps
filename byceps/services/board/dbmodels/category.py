"""
byceps.services.board.dbmodels.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import DbUser

from ..transfer.models import BoardID

from .board import DbBoard


class DbCategory(db.Model):
    """A category for topics."""

    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('board_id', 'slug'),
        db.UniqueConstraint('board_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    board_id = db.Column(db.UnicodeText, db.ForeignKey('boards.id'), index=True, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.UnicodeText, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_posting_updated_at = db.Column(db.DateTime)
    last_posting_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_posting_updated_by = db.relationship(DbUser)
    hidden = db.Column(db.Boolean, default=False, nullable=False)

    board = db.relationship(
        DbBoard,
        backref=db.backref(
            'categories',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self, board_id: BoardID, slug: str, title: str, description: str
    ) -> None:
        self.board_id = board_id
        self.slug = slug
        self.title = title
        self.description = description

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('board', self.board_id) \
            .add_with_lookup('slug') \
            .add_with_lookup('title') \
            .build()
