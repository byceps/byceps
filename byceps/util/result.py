"""
byceps.util.result
~~~~~~~~~~~~~~~~~~

A result wrapper that represents either the result value or an error.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generic, Literal, NoReturn, TypeVar, Union


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

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        return self._value

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

    def unwrap(self) -> NoReturn:
        raise UnwrapError(self)

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        return default()

    def __repr__(self) -> str:
        return f'Err({self._error})'


Result = Union[Ok[T], Err[E]]


class UnwrapError(Exception):
    ...
