from __future__ import annotations
from dataclasses import dataclass
from computer import Computer
from typing import TYPE_CHECKING, Union
from branch_decision import BranchDecision

if TYPE_CHECKING:
    from virus import VirusType

__authors__ = " "

@dataclass
class RouteSplit:

    """
    This class represents a split component in the route.
    
       _____top______
      /              \
    -<                >-following-
      \____bottom____/

    """

    top: Route
    bottom: Route
    following: Route

    def remove_branch(self) -> RouteStore:
        """
        Removes the branch, should just leave the remaining following route.

        param: self
        return: RouteStore object
        post: 

        """

        return self.following.store

@dataclass
class RouteSeries:
    """
    This class represents a computer, followed by the rest of the route.

    --computer--following--

    """

    computer: Computer
    following: Route

    def remove_computer(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Removing the computer at the beginning of this series.

        param: self
        return: The resulting RouteStore object.
        post: Creating a new route where a computer is removed from the beginning of the series.

        """
        return Route(Route(None), self.following.store) 


    def add_computer_before(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer in series before the current one.

        param: self, computer (Computer): The computer to add.
        return: The resulting RouteStore object.
        post: 
        """
        
        # PREVIOUS ORDER: route -> following route
        # NEW ORDER: new computer -> route -> following route
        new_series = RouteSeries(computer, Route(self))

        return new_series

    def add_computer_after(self, computer: Computer) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding a computer after the current computer, but before the following route.

        param: self, computer (Computer): The computer to add.
        return: The resulting RouteStore object.
        post: 
        """

        # The new computer is added after the current one but before the rest of the following route.
        # So we create a new RouteSeries with the new computer and the current following route.
        new_series_after = RouteSeries(computer, self.following)

        # Then, we create another RouteSeries with the current computer and the new_series_after as the following route.
        # This makes the new computer come right after the current computer.
        return RouteSeries(self.computer, Route(new_series_after))


    def add_empty_branch_before(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch, where the current routestore is now the following path.
        
        param:
        return:
        post:

        """

        # Create a new RouteSplit with two empty routes in the top and bottom,
        # and the current RouteSeries as the route that follows the split.
        new_split = RouteSplit(Route(None), Route(None), Route(self))

        # Return the new RouteSplit object, which is a valid RouteStore.
        return new_split

    def add_empty_branch_after(self) -> RouteStore:
        """
        Returns a route store which would be the result of:
        Adding an empty branch after the current computer, but before the following route.

        param:
        return:
        post:

        """
        new_split = RouteSplit(Route(None), Route(None), self.following)
        # Return a new RouteSeries with the current computer and the new RouteSplit.
        return RouteSeries(self.computer, Route(new_split))


RouteStore = Union[RouteSplit, RouteSeries, None]

@dataclass
class Route:
    """
    This class represents a Route.
    """

    store: RouteStore = None

    def add_computer_before(self, computer: Computer) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding a computer before everything currently in the route.

        param:
        return:
        post:

        """
        return Route(RouteSeries(computer, self))

    def add_empty_branch_before(self) -> Route:
        """
        Returns a *new* route which would be the result of:
        Adding an empty branch before everything currently in the route.

        param:
        return:
        post:

        """
        return Route(RouteSplit(Route(None), Route(None), self))

    def follow_path(self, virus_type: VirusType) -> None: #TODO
        """
        Follow a path and add computers according to a virus_type.
        
        param:
        return:
        post:

        """

        current_route = self
        branch_history = []
        stop = False

        while stop is not True:

            if type(current_route.store) == RouteSplit:
                
                # Remember the branch we are in as will need to find its follow path later.
                branch_history.append(current_route)
                decision = virus_type.select_branch(current_route.store.top, current_route.store.bottom)

                # Follow the selected branch as per the virus' decision.
                if decision == BranchDecision.TOP:
                    current_route = current_route.store.top
                elif decision == BranchDecision.BOTTOM:
                    current_route = current_route.store.bottom
                elif decision == BranchDecision.STOP:
                    stop = True

            elif type(current_route.store) == RouteSeries:
                
                # Store the current route's computer.
                current_computer = current_route.store.computer
                virus_type.add_computer(current_computer)

                # If it is the final computer we must stop.
                if current_computer.name == "final":
                    stop = True
                current_route = current_route.store.following
            
            # If the current route is Route(None):
            elif current_route.store == None:
                # We need to either exit the branch
                if len(branch_history) > 0:
                    branch_route = branch_history[-1].store
                    current_route = branch_route.following
                    branch_history.pop(-1)
                # Or if we are not in a branch, we need to exit.
                else:
                    stop = True

    def add_all_computers(self) -> list[Computer]:
        """
        Returns a list of all computers on the route.
        
        param:
        return:
        post:

        """
        if self.store is None:
            return []
        elif type(self.store) == RouteSeries:
            return [self.store.computer] + self.store.following.add_all_computers()
        elif type(self.store) == RouteSplit:
            return (self.store.top.add_all_computers() +
                    self.store.bottom.add_all_computers() +
                    self.store.following.add_all_computers())
        return []