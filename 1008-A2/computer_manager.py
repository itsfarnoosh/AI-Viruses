from __future__ import annotations
from computer import Computer


class ComputerManager:

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        # Add a Computer object to the list.
        self.computers.append(computer)

    def remove_computer(self, computer: Computer) -> None:
        # Remove a specific Computer object from the list.
        if computer in self.computers:
            self.computers.remove(computer)

    def edit_computer(self, old: Computer, new: Computer) -> None:
        # Replace an old Computer with a new one.
        try:
            index = self.computers.index(old)
            self.computers[index] = new
        except ValueError:
            # Optionally, handle the case where the old computer is not found.
            print(f"Computer not found in the list: {old}")

    def computers_with_difficulty(self, diff: int) -> list[Computer]:
        # Filter and return computers by specified hacking difficulty.
        return [comp for comp in self.computers if comp.hacking_difficulty == diff]

    def group_by_difficulty(self) -> list[list[Computer]]:
        # Group and sort computers by hacking difficulty.
        grouped = {}
        for comp in self.computers:
            difficulty = comp.hacking_difficulty
            if difficulty not in grouped:
                grouped[difficulty] = []
            grouped[difficulty].append(comp)
        # Convert dictionary to sorted list of lists by difficulty
        return [grouped[key] for key in sorted(grouped)]
