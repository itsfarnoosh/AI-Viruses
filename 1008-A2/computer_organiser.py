from __future__ import annotations

from computer import Computer
from algorithms import binary_search

class ComputerOrganiser:

    def __init__(self) -> None:
        """
        Initializes a new ComputerOrganiser instance.
        
        Time Complexity: O(1), as it just initializes an empty list.
        """
        self.sorted_computers = []

    def add_computers(self, computers: list[Computer]) -> None:
        """
        Adds a list of computers to the organiser in sorted order.
        
        Time Complexity: 
        - Sorting the new computers: O(M log M), where M is the number of new computers.
        - Merging the new sorted computers with the existing sorted list: O(M + N),
          where N is the total number of computers already in the organiser.
        Overall: O(M log M + N)
        """
        # Sort the incoming computers based on the criteria: O(M log M)
        computers.sort(key=lambda c: (c.hacking_difficulty, c.risk_factor, c.name))

        # Merge the newly sorted computers with the already sorted list: O(M + N)
        new_sorted_list = []
        i = j = 0
        while i < len(self.sorted_computers) and j < len(computers):
            if (self.sorted_computers[i].hacking_difficulty, self.sorted_computers[i].risk_factor, self.sorted_computers[i].name) <= \
               (computers[j].hacking_difficulty, computers[j].risk_factor, computers[j].name):
                new_sorted_list.append(self.sorted_computers[i])
                i += 1
            else:
                new_sorted_list.append(computers[j])
                j += 1
        # Add any remaining items from the lists
        new_sorted_list.extend(self.sorted_computers[i:])
        new_sorted_list.extend(computers[j:])
        
        self.sorted_computers = new_sorted_list

    def cur_position(self, computer: Computer) -> int:
        """
        Finds the current position of a computer in the sorted list.
        
        Time Complexity: O(log N), where N is the total number of computers
        already in the organiser. This is because a binary search is used
        to find the position.
        """
        # Perform binary search within the list: O(log N)
        left, right = 0, len(self.sorted_computers) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.sorted_computers[mid] == computer:
                return mid
            elif (self.sorted_computers[mid].hacking_difficulty, self.sorted_computers[mid].risk_factor, self.sorted_computers[mid].name) < \
                 (computer.hacking_difficulty, computer.risk_factor, computer.name):
                left = mid + 1
            else:
                right = mid - 1
        raise KeyError("Computer not found in the organiser.")