from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")


class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self, level: int = 0,parent: "InfiniteHashTable" = None) -> None:
        self.array: ArrayR[tuple[K, V] | None] = ArrayR(self.TABLE_SIZE)
        self.count = 0# Number of items stored in the table
        self.level = level  # Hierarchy level
        self.parent= parent
    
    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        index = self.hash(key)
        item = self.array[index]

        if isinstance(item, InfiniteHashTable):
            return item[key]
        elif item is not None and item[0] == key:
            return item[1]
        else:
            raise KeyError(f"Key not found: {key}")
        
    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        index = self.hash(key)
        item = self.array[index]
        

        if isinstance(item, InfiniteHashTable):
            item[key] = value  # Recursive set, count managed by sub-table
            self.count += 1
        elif item is None:
            self.array[index] = (key, value)
            self.count += 1  # Increment only if a new item is added
        elif item[0] == key:
            self.array[index] = (key, value)  # Update existing item, count unchanged
            
        else:
            # Handle collisions by creating a nested hash table
            new_table = InfiniteHashTable(self.level + 1, self)
            new_table[item[0]] = item[1]
            new_table[key] = value
            self.array[index] = new_table
            self.count += 1  # Increment for the new key; existing moved to new_table
    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        index = self.hash(key)
        item = self.array[index]

        if isinstance(item, InfiniteHashTable):
            del item[key]
            if len(item) == 1:  # Collapse sub-table into a single entry
                for sub_key in range(item.TABLE_SIZE):
                    sub_item = item.array[sub_key]
                    if sub_item is not None:
                        self.array[index] = sub_item
                        break
            if len(item) == 0:  # If the sub-table is empty after deletion
                self.array[index] = None
            self.count -= 1
            # Check for collapsing into parent if this table now has one item
            if self.count == 1 and self.parent:
                for parent_index in range(self.parent.TABLE_SIZE):
                    if self.parent.array[parent_index] is self:
                        for i in range(self.TABLE_SIZE):
                            if self.array[i] is not None:
                                self.parent.array[parent_index] = self.array[i]
                                break

        elif item is not None and item[0] == key:
            self.array[index] = None
            self.count -= 1
            if self.count == 1 and self.parent:
                for parent_index in range(self.parent.TABLE_SIZE):
                    if self.parent.array[parent_index] is self:
                        for i in range(self.TABLE_SIZE):
                            if self.array[i] is not None:
                                self.parent.array[parent_index] = self.array[i]
                                break

        else:
            raise KeyError("Key not found")

    def __len__(self) -> int:
         return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()

    def get_location(self, key) -> list[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        location = []
        current_table = self
        while isinstance(current_table, InfiniteHashTable):
            index = current_table.hash(key)
            location.append(index)
            item = current_table.array[index]

            if isinstance(item, InfiniteHashTable):
                current_table = item
            elif item is not None and item[0] == key:
                return location
            else:
                break  # Stop if the next level does not contain the key

        raise KeyError(f"Key not found: {key}")
    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        """
        # If current is None, we start from the top-level table
        if current is None:
            current = self

        keys = []
        for item in current.array:
            if isinstance(item, tuple) and item[0] is not None:
                # Direct key-value pair, add the key
                keys.append(item[0])
            elif isinstance(item, InfiniteHashTable):
                # Sub-table found, recurse into it
                keys.extend(self.sort_keys(current=item))
        
        # Only sort at the top level for efficiency
        if current is self:
            keys.sort()

        return keys
        
        