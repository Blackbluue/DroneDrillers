"""Overlord, who oversees atron drones and assigns tasks to them."""

from __future__ import annotations

from queue import SimpleQueue
from typing import TYPE_CHECKING

from utils import Context, MapData

from .atron import Atron
from .drones import Drone

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Optional, Type

DEFAULT_HEALTH = 10

class Overlord(Atron):
    """Overlord, who oversees atron drones and assigns tasks to them."""

    def __init__(self) -> None:
        """Initialize the Overlord."""
        super().__init__(DEFAULT_HEALTH)
        self.drones: MutableMapping[int, Drone] = {}
        # a drone id as key and drone as value

        self._idle_drones: MutableMapping[Type[Drone], set[Drone]] = {}
        self._update_queue: SimpleQueue[tuple[MapData, Drone, Context]] = (
            SimpleQueue()
        )
        # a queue of map updates from drones

        self._pickup_queue: SimpleQueue[tuple[MapData, Drone]] = SimpleQueue()
        # a queue of pick up requests from drones

        self._mining_map: MapData | None = None
        # the current mining map

    def set_map(self, mining_map: MapData) -> None:
        """Register the mining map to the overlord.

        Args:
            mining_map (MapData): The map to register.
        """
        self._mining_map = mining_map

    def action(self, context=None) -> str:
        # sourcery skip: assign-if-exp, reintroduce-else
        """Perform some action, based on the context of the situation.

        Args:
            context (Context): Context surrounding the overlord;
                currently unused

        Returns:
            str: The action for the overlord to perform
        """
        return "NONE"
