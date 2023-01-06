"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class Tourney:
    id: str
    title: str


@dataclass(frozen=True)
class Participant:
    id: str
    name: str


@dataclass(frozen=True)
class Match:
    id: str
    tourney_id: str
    participant1_id: str
    participant1_name: str
    participant2_id: str
    participant2_name: str


@pytest.fixture(scope='package')
def make_tourney():
    def _wrapper(tourney_id: str, title: str) -> Tourney:
        return Tourney(tourney_id, title)

    yield _wrapper


@pytest.fixture(scope='package')
def make_participant():
    def _wrapper(participant_id: str, name: str) -> Participant:
        return Participant(participant_id, name)

    return _wrapper


@pytest.fixture(scope='package')
def make_match():
    def _wrapper(
        match_id: str,
        tourney: Tourney,
        participant1: Participant,
        participant2: Participant,
    ) -> Match:
        return Match(
            match_id,
            tourney.id,
            participant1.id,
            participant1.name,
            participant2.id,
            participant2.name,
        )

    return _wrapper
