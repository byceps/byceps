"""
byceps.services.site_navigation.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.ext.orderinglist import ordering_list

from ...database import db, generate_uuid

from ..language.dbmodels import DbLanguage
from ..site.models import SiteID

from .models import NavItemID, NavItemTargetType, NavMenuID


class DbNavMenu(db.Model):
    """A navigation menu."""

    __tablename__ = 'site_nav_menus'
    __table_args__ = (db.UniqueConstraint('site_id', 'name', 'language_code'),)

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    site_id = db.Column(
        db.UnicodeText, db.ForeignKey('sites.id'), index=True, nullable=False
    )
    name = db.Column(db.UnicodeText, index=True, nullable=False)
    language_code = db.Column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
        nullable=False,
    )
    language = db.relationship(DbLanguage)
    hidden = db.Column(db.Boolean, nullable=False)

    def __init__(
        self, site_id: SiteID, name: str, language_code: str, hidden: bool
    ) -> None:
        self.site_id = site_id
        self.name = name
        self.language_code = language_code
        self.hidden = hidden


class DbNavItem(db.Model):
    """An item of a navigation menu."""

    __tablename__ = 'site_nav_menu_items'
    __table_args__ = (
        db.UniqueConstraint('menu_id', 'parent_item_id', 'position'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    menu_id = db.Column(
        db.Uuid, db.ForeignKey('site_nav_menus.id'), index=True, nullable=False
    )
    menu = db.relationship(
        DbNavMenu,
        backref=db.backref(
            'items',
            order_by='byceps.services.site_navigation.dbmodels.DbNavItem.position',
            collection_class=ordering_list('position', count_from=1),
        ),
    )
    parent_item_id = db.Column(
        db.Uuid,
        db.ForeignKey('site_nav_menu_items.id'),
        index=True,
        nullable=True,
    )
    position = db.Column(db.Integer, nullable=False)
    _target_type = db.Column('target_type', db.UnicodeText, nullable=False)
    target = db.Column(db.UnicodeText, nullable=False)
    label = db.Column(db.UnicodeText, nullable=False)
    current_page_id = db.Column(db.UnicodeText, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        menu_id: NavMenuID,
        parent_item_id: Optional[NavItemID],
        target_type: NavItemTargetType,
        target: str,
        label: str,
        current_page_id: str,
        hidden: bool,
    ) -> None:
        self.menu_id = menu_id
        self.parent_item_id = parent_item_id
        self.target_type = target_type
        self.target = target
        self.label = label
        self.current_page_id = current_page_id
        self.hidden = hidden

    @hybrid_property
    def target_type(self) -> NavItemTargetType:
        return NavItemTargetType[self._target_type]

    @target_type.setter
    def target_type(self, target_type: NavItemTargetType) -> None:
        assert target_type is not None
        self._target_type = target_type.name
