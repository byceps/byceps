"""
byceps.services.guest_server.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
import ipaddress
from typing import Optional, TYPE_CHECKING

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

from .models import AddressID, IPAddress, ServerID


class DbGuestServerSetting(db.Model):
    """A party-specific setting for guest servers."""

    __tablename__ = 'guest_server_settings'

    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), primary_key=True
    )
    _netmask: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'netmask', postgresql.INET
    )
    _gateway: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'gateway', postgresql.INET
    )
    _dns_server1: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'dns_server1', postgresql.INET
    )
    _dns_server2: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'dns_server2', postgresql.INET
    )
    domain: Mapped[Optional[str]] = mapped_column(db.UnicodeText)  # noqa: UP007

    def __init__(self, party_id: PartyID) -> None:
        self.party_id = party_id

    @hybrid_property
    def netmask(self) -> IPAddress | None:
        if not self._netmask:
            return None

        return ipaddress.ip_address(self._netmask)

    @netmask.setter
    def netmask(self, netmask: IPAddress | None) -> None:
        self._netmask = str(netmask) if netmask else None

    @hybrid_property
    def gateway(self) -> IPAddress | None:
        if not self._gateway:
            return None

        return ipaddress.ip_address(self._gateway)

    @gateway.setter
    def gateway(self, ip_address: IPAddress | None) -> None:
        self._gateway = str(ip_address) if ip_address else None

    @hybrid_property
    def dns_server1(self) -> IPAddress | None:
        if not self._dns_server1:
            return None

        return ipaddress.ip_address(self._dns_server1)

    @dns_server1.setter
    def dns_server1(self, ip_address: IPAddress | None) -> None:
        self._dns_server1 = str(ip_address) if ip_address else None

    @hybrid_property
    def dns_server2(self) -> IPAddress | None:
        if not self._dns_server2:
            return None

        return ipaddress.ip_address(self._dns_server2)

    @dns_server2.setter
    def dns_server2(self, ip_address: IPAddress | None) -> None:
        self._dns_server2 = str(ip_address) if ip_address else None

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('party_id').build()


class DbGuestServer(db.Model):
    """A guest server."""

    __tablename__ = 'guest_servers'

    id: Mapped[ServerID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    owner_id: Mapped[UserID] = mapped_column(db.Uuid, db.ForeignKey('users.id'))
    description: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )
    notes_owner: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )
    notes_admin: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )
    approved: Mapped[bool]
    checked_in_at: Mapped[Optional[datetime]]  # noqa: UP007
    checked_out_at: Mapped[Optional[datetime]]  # noqa: UP007

    def __init__(
        self,
        server_id: ServerID,
        party_id: PartyID,
        created_at: datetime,
        creator_id: UserID,
        owner_id: UserID,
        description: str,
        *,
        notes_owner: str | None = None,
        notes_admin: str | None = None,
    ) -> None:
        self.id = server_id
        self.party_id = party_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.owner_id = owner_id
        self.description = description
        self.notes_owner = notes_owner
        self.notes_admin = notes_admin
        self.approved = False
        self.checked_in_at = None
        self.checked_out_at = None

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()


class DbGuestServerAddress(db.Model):
    """An guest server's IPv4 address and optional DNS name."""

    __tablename__ = 'guest_server_addresses'

    id: Mapped[AddressID] = mapped_column(db.Uuid, primary_key=True)
    server_id: Mapped[ServerID] = mapped_column(
        db.Uuid, db.ForeignKey('guest_servers.id'), index=True
    )
    server: Mapped[DbGuestServer] = relationship(
        DbGuestServer, backref='addresses'
    )
    created_at: Mapped[datetime] = mapped_column(db.DateTime)
    _ip_address: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'ip_address', postgresql.INET
    )
    hostname: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )
    _netmask: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'netmask', postgresql.INET
    )
    _gateway: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'gateway', postgresql.INET
    )

    def __init__(
        self,
        address_id: AddressID,
        server_id: ServerID,
        created_at: datetime,
        *,
        ip_address: IPAddress | None = None,
        hostname: str | None = None,
        netmask: IPAddress | None = None,
        gateway: IPAddress | None = None,
    ) -> None:
        self.id = address_id
        self.server_id = server_id
        self.created_at = created_at
        self.ip_address = ip_address
        self.hostname = hostname
        self.netmask = netmask
        self.gateway = gateway

    @hybrid_property
    def ip_address(self) -> IPAddress | None:
        if not self._ip_address:
            return None

        return ipaddress.ip_address(self._ip_address)

    @ip_address.setter
    def ip_address(self, ip_address: IPAddress | None) -> None:
        self._ip_address = str(ip_address) if ip_address else None

    @hybrid_property
    def netmask(self) -> IPAddress | None:
        if not self._netmask:
            return None

        return ipaddress.ip_address(self._netmask)

    @netmask.setter
    def netmask(self, netmask: IPAddress | None) -> None:
        self._netmask = str(netmask) if netmask else None

    @hybrid_property
    def gateway(self) -> IPAddress | None:
        if not self._gateway:
            return None

        return ipaddress.ip_address(self._gateway)

    @gateway.setter
    def gateway(self, ip_address: IPAddress | None) -> None:
        self._gateway = str(ip_address) if ip_address else None

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
