"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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


@pytest.fixture(scope='session')
def make_tourney():
    def _wrapper(tourney_id, title):
        return Tourney(tourney_id, title)

    yield _wrapper


@pytest.fixture(scope='session')
def make_participant():
    def _wrapper(participant_id, name):
        return Participant(participant_id, name)

    yield _wrapper


@pytest.fixture(scope='session')
def make_match():
    def _wrapper(match_id, tourney, participant1, participant2):
        return Match(
            match_id,
            tourney.id,
            participant1.id,
            participant1.name,
            participant2.id,
            participant2.name,
        )

    yield _wrapper
