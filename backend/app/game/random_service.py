from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class RandomService:
    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def roll(self) -> float:
        return self._random.random()

    def randint(self, minimum: int, maximum: int) -> int:
        return self._random.randint(minimum, maximum)

    def choice(self, values: Sequence[T]) -> T:
        return self._random.choice(values)

