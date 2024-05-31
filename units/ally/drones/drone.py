"""Contains the Drone class and the drone State class"""

from units.ally.atron import Atron
from utils import Icon


class Drone(Atron):
    @property
    def icon(self) -> Icon:
        """The icon of this drone type."""
        raise NotImplementedError("Drone subtypes must implement icon")
