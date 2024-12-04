from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        if sizes is not None:
            self.TABLE_SIZES = sizes

        if internal_sizes is not None:
            self.internal_sizes = internal_sizes
        else:
            self.internal_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array: ArrayR[tuple[K1, V] | None] | None = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2 | None, is_insert: bool) -> tuple[int, int] | int:
        """
        Find the correct position for this key in the hash table using linear probing.
        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        # Calculate the top level index.
        top_level_index = self.hash1(key1)

        # If key2 is None, then return the top-level index.
        if key2 is None:
            if not is_insert and (self.array[top_level_index] is None or self.array[top_level_index][0] != key1):
                raise KeyError(f"Top-level key {key1} not found")
            return top_level_index

        # Linear probe on the table's top-level.
        while self.array[top_level_index] is not None and self.array[top_level_index][0] != key1:
            top_level_index = (top_level_index + 1) % len(self.array)  # Wrap around if necessary

        if self.array[top_level_index] is None:
            if is_insert:
                # Create a new sub-table if necessary.
                self.array[top_level_index] = (key1, LinearProbeTable[K2, V](self.internal_sizes))
            else:
                raise KeyError(f"Key pair ({key1}, {key2}) not found")
        
        # Get the sub-table.
        sub_table = self.array[top_level_index][1]
        # Override the sub table's hash function to follow the hash2 algorithm.
        sub_table.hash = lambda k, tab= sub_table:self.hash2(k,tab)

        """
        while sub_table.array[bottom_level_index] is not None and sub_table.array[bottom_level_index][1] != key2:
            bottom_level_index = (bottom_level_index + 1) % len(sub_table.array)  # Wrap around if necessary
            
            if sub_table.array[bottom_level_index] is None and not is_insert:
                raise KeyError(f"Key pair ({key1}, {key2}) not found")
            if is_insert and sub_table.array[bottom_level_index] is None:
                # Increment the sub-table count when a new key is inserted
                sub_table.count += 1
        """
        # Use the inner table's linear probing method to find the index to insert (or find) key2 in.
        try:
            bottom_level_index = sub_table._linear_probe(key2, is_insert)
        except FullError:
            # If the internal table is full, the method will raise a FullError. 
            # The internal table must be rehashed using its own rehash method.
            sub_table._rehash()
            # Probe again to find a position for key2 in the sub-table.
            sub_table._linear_probe(key2, is_insert)

        return top_level_index, bottom_level_index
        
    #passed 
    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        # should return an iterator that yields the keys one by one rather than searching the entire table at the start.
        # You should NOT get all the keys at the start and just iterate through those. 
        #That won't be very efficient. Your iterator should only get the next item when it's needed.
        if key is None:
            # Iterate over the top-level hash table and yield each non-None key
            for entry in self.array:
                if entry is not None:
                    yield entry[0]
                break
        else:
            # Iterate to find the specific top-level key and then iterate over its sub-table
            found = False
            for entry in self.array:
                if entry is not None and entry[0] == key:
                    # Once the correct sub-table is found, yield each key from this sub-table
                    found = True
                    for sub_entry in entry[1].array:
                        if sub_entry is not None:
                            yield sub_entry[0]
                        break
            if not found:
                # If the loop completes without finding the key, raise KeyError
                raise KeyError(f"Top-level key {key} not found in the hash table.")

    #passed 
    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        # should return an iterator that yields the values one by one rather than searching the entire table at the start.
        # You should NOT get all the values at the start and just iterate through those. 
        #That won't be very efficient. Your iterator should only get the next item when it's needed.
        if key is None:
            # Iterate over the entire hash table to yield all values from all sub-tables
            for entry in self.array:
                if entry is not None:
                    sub_table = entry[1]
                    for sub_entry in sub_table.array:
                        if sub_entry is not None:
                            yield sub_entry[1]
                        
        else:
            # Iterate to find the specific top-level key and then yield values from its sub-table
            found = False
            for entry in self.array:
                if entry is not None and entry[0] == key:
                    found = True
                    sub_table = entry[1]
                    for sub_entry in sub_table.array:
                        if sub_entry is not None:
                            yield sub_entry[1]
                    break
            if not found:
                # If the loop completes without finding the key, raise KeyError
                raise KeyError(f"Top-level key {key} not found in the hash table.")


    def keys(self, key: K1 | None = None) -> list[K1 | K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        #If key = None, return all top-level keys in the hash table
        top_level_keys = []
        if key == None:
            for x in range(self.table_size):
                if self.array[x] is not None:
                    top_level_keys.append(self.array[x][0])
            return top_level_keys
        #If key != None ==>return all low-level keys in the sub-table of top-level key.
            #In the case that the key isn't found, raise KeyError.
        elif key != None:
            for x in range(self.table_size):
                if self.array[x] is not None and self.array[x][0] == key:
                    sub_table = self.array[x][1]
                    # Collect all second-level keys from the sub-table
                    bottom_level_keys = [sub_entry[0] for sub_entry in sub_table.array if sub_entry is not None]
                    return bottom_level_keys
            # If the loop completes without finding the key, it wasn't present
            raise KeyError(f"Key {key} not found in the top-level table.")
            



    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        all_values = []
        # If key is None, return all values in all entries in the entire double key hash table (including both the top level and bottom levels)
        if key is None:
            for entry in self.array:
                if entry is not None and entry[1] is not None:  # Check if entry and sub-table are not None
                    for sub_entry in entry[1].array:  # entry[1] should be a sub-table
                        if sub_entry is not None:
                            all_values.append(sub_entry[1])  # sub_entry[1] should be the value of the bottom-level key
            return all_values

        # If key is not None, restrict to all values in the sub-table of top-level key.
        # In the case that the key isn't found, raise KeyError.
        else:
            found = False
            for entry in self.array:
                if entry is not None and entry[0] == key:  # Check if top-level key matches
                    if entry[1] is not None:  # Ensure the sub-table exists
                        found = True
                        for sub_entry in entry[1].array:
                            if sub_entry is not None:
                                all_values.append(sub_entry[1])
                        break  # Stop searching after finding and processing the correct sub-table

            if not found:  # If no top-level entry matched the provided key
                raise KeyError(f"Top-level key {key} not found in the hash table.")

            return all_values



    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """

        position1, position2 = self._linear_probe(key[0], key[1], False)
        return self.array[position1][1].array[position2][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        key1, key2 = key
        position1, position2 = self._linear_probe(key1, key2, True)
        sub_table = self.array[position1][1]

        if sub_table.is_empty():
            self.count += 1

        sub_table[key2] = data

        # resize if necessary
        if len(self) > self.table_size / 2:
            self._rehash()
    #passed 
    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.
        :param key: A tuple containing key1 and key2 indicating the top-level and second-level keys respectively.
        :raises KeyError: when the key doesn't exist.
        """
        #if the key1,key2 pair was the only key1 element in the table ==> you should clear out the entirety of that internal table 
            #so that a new key1 with the same hash can be inserted in that position. 
        key1, key2 = key
        # Find the top-level key
        for i in range(len(self.array)):
            if self.array[i] is not None and self.array[i][0] == key1:
                sub_table = self.array[i][1]
                # Attempt to delete key2 from the sub-table
                try:
                    del sub_table[key2]  # Assuming sub_table supports del operation directly
                    # Check if the sub-table is now empty
                    if len(sub_table) == 0:
                        # Clear the entry if the sub-table is empty
                        self.array[i] = None
                    return
                except KeyError:
                    # If the sub-table does not contain key2, raise KeyError
                    raise KeyError(f"Key pair ({key1}, {key2}) not found in the hash table.")

        # If the loop completes without deleting, key1 was not found
        raise KeyError(f"Top-level key {key1} not found in the hash table.")
                
    def _rehash(self) -> None:
        """
        Need to resize the top-level table and potentially reinsert all values if their positions change. 
        Also checks if sub-tables need rehashing based on their load factor.

        :complexity best: O(N*hash(K)) where N is the number of entries and K is the key complexity during hashing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) where comp(K) represents complexity due to probing in a crowded table.
        """
        old_array = self.array  # Store the current array to reinsert its elements into a new, larger array.
        self.size_index += 1  # Increment the index to use the next size for the hash table from the predefined sizes list.

        # Check if we've reached the maximum allowed size index.
        if self.size_index >= len(self.TABLE_SIZES):
            self.size_index -= 1  # If so, revert the increment to stay within bounds and exit the method.
            return

        # Allocate a new array with the next size to accommodate more entries or reduce load.
        new_array = ArrayR(self.TABLE_SIZES[self.size_index])
        new_count = 0  # This will count the number of actual used entries in the new array.

        # Iterate through each item in the old array.
        for item in old_array:
            if item is not None:  # Check if the current slot is not empty.
                key1, sub_table = item  # Unpack the tuple containing the key and its corresponding sub-table.

                # Check if the load factor of the sub-table exceeds 0.5 and needs rehashing.
                if len(sub_table) > len(sub_table.array) / 2:
                    sub_table._rehash()  # Trigger rehash of the sub-table.

                # Compute a new hash index for key1 in the resized top-level table.
                new_index = self.hash1(key1)
                # Resolve collisions using linear probing.
                while new_array[new_index] is not None:
                    new_index = (new_index + 1) % len(new_array)  # Ensure wrapping at the boundary of the array.

                # Place the item at its new position in the resized array.
                new_array[new_index] = (key1, sub_table)
                new_count += 1  # Increment the count of used slots.

        # Replace the old array with the newly sized array and update the count of items.
        self.array = new_array
        self.count = new_count
    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()
    