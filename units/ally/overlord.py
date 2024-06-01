from __future__ import annotations

from queue import SimpleQueue
from typing import TYPE_CHECKING

from utils import Context, Map

from .atron import Atron
from .drones import Drone

if TYPE_CHECKING:
    from typing import Optional, Type

    from gui.dashboard import Dashboard


class Overlord(Atron):
    """Overlord, who oversees atron drones and assigns tasks to them."""

    def __init__(
        self,
        total_ticks: int,
        refined_minerals: int,
        dashboard: Dashboard,
    ) -> None:
        """Initialize the Overlord.

        Args:
            total_ticks (int): Total ticks allowed for mining.
            refined_minerals (int): Total given minerals.
            dashboard (Dashboard): The GUI dashboard.
        """
        self.dashboard = dashboard
        self.drones: dict[int, Drone] = {}
        # a drone id as key and drone as value

        self._deployed: dict[int, Optional[Map]] = {}
        # a drone id as key and map id as value

        self._idle_drones: dict[Type[Drone], set[Drone]] = {}
        self._update_queue: SimpleQueue[tuple[Map, Drone, Context]] = (
            SimpleQueue()
        )
        # a queue of map updates from zerg drones

        self._pickup_queue: SimpleQueue[tuple[Map, Drone]] = SimpleQueue()
        # a queue of pick up requests from drones

        self._maps: dict[int, Map] = {}
        # a map id as key and Map as value

        # scouts, miners, classes = self._create_drone_classes(refined_minerals)
        # for _ in range(scouts):
        #     self._create_drone(classes["Scout"])
        # for _ in range(miners):
        #     self._create_drone(classes["Miner"])

    def _create_drone_classes(self, minerals: int) -> tuple[int, int, dict]:
        """Create custom drone classes based on number of minerals.

        Args:
            minerals (int): Number of allotted minerals for drone
                creation

        Returns:
            List(Drone): List of drone classes containing a custom
            ScoutDrone and MinerDrone
        """
        return (0, 0, {})

    def add_map(self, map_id: int, summary: float) -> None:
        """Register ID for map and summary of mineral density.

        Args:
            map_id (int): The id of the map.
            summary (float): The density of minerals in the map.
        """
        physical_map = Map(map_id, summary)
        self._maps[map_id] = physical_map
        self.dashboard.create_map_gui(physical_map)
        self.dashboard.update_drone_table(self.drones.values())

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
