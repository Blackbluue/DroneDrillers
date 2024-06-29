"""Display information on the drones and actions in the game."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from utils.icon import Icon

from .label_counter import LabeledCounter

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from units.ally import Atron
    from units.ally.drones import Drone
    from utils.counter import Counter


class Dashboard(tk.Frame):
    """Display information on the drones and actions in the game."""

    def __init__(
        self,
        parent: tk.Tk,
        player_health: Counter,
        ticks: Counter,
        minerals: Counter,
    ) -> None:
        """Serve as the constructor for the Dashboard object.

        Args:
            parent (tk.Tk): Takes in a tk top level window
        """
        super().__init__(parent)

        self._player_health = LabeledCounter(
            self, "Player Health:", counter=player_health
        )
        self._ticks = LabeledCounter(self, "Ticks:", counter=ticks)
        self._refined = LabeledCounter(
            self, "Refined Minerals:", counter=minerals
        )

        drone_labels = {
            "Drone ID": 180,
            "Drone Type": 120,
            "Health": 90,
            "Capacity": 90,
        }
        self._drone_tree = self._make_tree(drone_labels)

        self._player_health.pack()
        self._ticks.pack()
        self._refined.pack()
        self._drone_tree.pack(side="left")

    def _make_tree(self, labels: Mapping[str, int]) -> ttk.Treeview:
        """Build trees for the dashboard to use.

        Dashboards typically serve as spreadsheets in the gui.
        Args:
            labels (Mapping[str, int]): Contains dictionaries and
                width values for each column.
        """
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#ad73ac")

        # Using treeview widget
        tree_view = ttk.Treeview(self, selectmode="browse")

        # Defining number of columns
        tree_view["columns"] = tuple(labels)

        # Defining heading
        tree_view["show"] = "headings"

        for column_count, (column, width) in enumerate(labels.items()):
            string_column = str(column_count)
            tree_view.column(string_column, width=width, anchor="se")
            tree_view.heading(string_column, text=column)
        return tree_view

    def add_atron_to_tree(self, new_drone: Atron) -> None:
        """Add a drone to the drone tree in the gui.

        Args:
            new_drone (Atron) : This is the atron we are adding to the tree in
                the dashboard.
        """
        type_of_drone = type(new_drone).__name__
        self._drone_tree.insert(
            "",
            "end",
            text="Listbox",
            values=(
                id(new_drone),
                type_of_drone,
                new_drone.health,
                new_drone.payload.get(),
            ),
        )

    def update_drone_table(self, drones: Iterable[Drone]) -> None:
        """Clear drone table and adds a new list of drones to the table.

        Args:
            drones (Iterable[Drone]) : The list of drones.
        """
        for entry in self._drone_tree.get_children():
            self._drone_tree.delete(entry)
        for drone in drones:
            self.add_atron_to_tree(drone)
