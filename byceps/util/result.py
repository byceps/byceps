"""
byceps.util.result
~~~~~~~~~~~~~~~~~~

A result wrapper that represents either the result value or an error.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Literal, TypeVar, Union
from typing_extensions import Never


T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


@dataclass(eq=True, frozen=True)
class Ok(Generic[T]):
    _value: T

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def map(self, f: Callable[[T], U]) -> Ok[U]:
        return Ok(f(self._value))

    def map_or_else(self, default: Callable[[T], U], f: Callable[[T], U]) -> U:
        return f(self._value)

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> Never:
        raise UnwrapError(self, '`unwrap_err()` called on `Ok` value')

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        return self._value

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return f(self._value)

    def __repr__(self) -> str:
        return f'Ok({self._value})'


@dataclass(eq=True, frozen=True)
class Err(Generic[E]):
    _error: E

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def map(self, f: Callable[[T], U]) -> Err[E]:
        return self

    def map_or_else(self, default: Callable[[E], U], f: Callable[[T], U]) -> U:
        return default(self._error)

    def unwrap(self) -> Never:
        raise UnwrapError(self)

    def unwrap_err(self) -> E:
        return self._error

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, default: Callable[[E], T]) -> T:
        return default(self._error)

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return self

    def __repr__(self) -> str:
        return f'Err({self._error})'


Result = Union[Ok[T], Err[E]]


class UnwrapError(Exception):
    ...
