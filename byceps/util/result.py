"""
byceps.util.result
~~~~~~~~~~~~~~~~~~

A result wrapper that represents either the result value or an error.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Never


@dataclass(eq=True, frozen=True)
class Ok[T]:
    _value: T

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def map[U](self, f: Callable[[T], U]) -> Ok[U]:
        return Ok(f(self._value))

    def map_err[E, U](self, f: Callable[[E], U]) -> Ok[T]:
        return self

    def map_or_else[E, U](
        self, f: Callable[[T], U], default: Callable[[E], U]
    ) -> U:
        return f(self._value)

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> Never:
        raise UnwrapError(self, '`unwrap_err()` called on `Ok` value')

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        return self._value

    def and_then[E, U](self, f: Callable[[T], Result[U, E]]) -> Result:
        return f(self._value)

    def __repr__(self) -> str:
        return f'Ok({self._value})'


@dataclass(eq=True, frozen=True)
class Err[E]:
    _error: E

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def map[T, U](self, f: Callable[[T], U]) -> Err[E]:
        return self

    def map_err[U](self, f: Callable[[E], U]) -> Err[U]:
        return Err(f(self._error))

    def map_or_else[T, U](
        self, f: Callable[[T], U], default: Callable[[E], U]
    ) -> U:
        return default(self._error)

    def unwrap(self) -> Never:
        raise UnwrapError(self)

    def unwrap_err(self) -> E:
        return self._error

    def unwrap_or[T](self, default: T) -> T:
        return default

    def unwrap_or_else[T](self, default: Callable[[E], T]) -> T:
        return default(self._error)

    def and_then[T, U](self, f: Callable[[T], Result[U, E]]) -> Result:
        return self

    def __repr__(self) -> str:
        return f'Err({self._error})'


type Result[T, E] = Ok[T] | Err[E]


class UnwrapError(Exception): ...
