from __future__ import annotations
from abc import ABC, abstractmethod
from computer import Computer
from route import Route, RouteSeries, RouteSplit
from branch_decision import BranchDecision


class VirusType(ABC):

    def __init__(self) -> None:
        self.computers = []

    def add_computer(self, computer: Computer) -> None:
        self.computers.append(computer)

    @abstractmethod
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        raise NotImplementedError()


class TopVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the top branch
        return BranchDecision.TOP


class BottomVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        # Always select the bottom branch
        return BranchDecision.BOTTOM


class LazyVirus(VirusType):
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Try looking into the first computer on each branch,
        take the path of the least difficulty.
        """
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries

        if top_route and bot_route:
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            if top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                return BranchDecision.TOP
            elif top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                return BranchDecision.BOTTOM
            else:
                return BranchDecision.STOP
        # If one of them has a computer, don't take it.
        # If neither do, then take the top branch.
        if top_route:
            return BranchDecision.BOTTOM
        return BranchDecision.TOP


class RiskAverseVirus(VirusType): 
    #TODO tested and comes up with error. Error seems to be discrepancy with list of computers passed
    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        This virus is risk averse and likes to choose the path with the lowest risk factor.

        :param:
        :return:
        :post:
        :comp best:
        :comp worst:
        """

        # Storing top and bottom branch route types.
        top_route = type(top_branch.store)
        bot_route = type(bottom_branch.store)

        # The case when both branches are RouteSeries:
        if top_route == RouteSeries and bot_route == RouteSeries:

            # Storing top and bottom branch computers
            top_comp = top_branch.store.computer
            bot_comp = bottom_branch.store.computer

            # The case when only ONE of the computers have 0.0 risk factor
            if top_comp.risk_factor == 0.0 and bot_comp.risk_factor != 0.0:
                # Return the path with 0.0 risk factor
                return BranchDecision.TOP
            elif top_comp.risk_factor != 0.0 and bot_comp.risk_factor == 0.0:
                return BranchDecision.BOTTOM
            
            else: 
                # The case when there both computers have a risk factor of 0.0
                if top_comp.risk_factor == 0.0 and bot_comp.risk_factor == 0.0:

                    # Check hacking difficulty, return the branch with lower value
                    if top_comp.hacking_difficulty > bot_comp.hacking_difficulty:
                        return BranchDecision.BOTTOM
                    elif top_comp.hacking_difficulty < bot_comp.hacking_difficulty:
                        return BranchDecision.TOP
                    
                    # If they are still tied
                    top_comp_value = max(top_comp.hacking_difficulty, (0.5*top_comp.hacked_value))
                    bot_comp_value = max(bot_comp.hacking_difficulty, (0.5*bot_comp.hacked_value))

                else: # The case when neither of the computers have a risk factor of 0
                    top_comp_value = max(top_comp.hacking_difficulty, (0.5*top_comp.hacked_value))/top_comp.risk_factor
                    bot_comp_value = max(bot_comp.hacking_difficulty, (0.5*bot_comp.hacked_value))/bot_comp.risk_factor
            
            # Take the path with the higher calculated value
            if top_comp_value > bot_comp_value:
                return BranchDecision.TOP
            elif top_comp_value < bot_comp_value:
                return BranchDecision.BOTTOM
            
            # In the case of a tie, take lower risk factor
            elif top_comp_value == bot_comp_value:

                if top_comp.risk_factor < bot_comp.risk_factor:
                    return BranchDecision.TOP
                elif top_comp.risk_factor > bot_comp.risk_factor:
                    return BranchDecision.BOTTOM
                elif top_comp.risk_factor == bot_comp.risk_factor:
                    # If still tied, STOP.
                    return BranchDecision.STOP

        # The case when one branch is a RouteSeries and the other is a RouteSplit:
        elif top_route == RouteSeries and bot_route == RouteSplit:
            # Return the branch that is a RouteSplit.
            return BranchDecision.BOTTOM
        elif top_route == RouteSplit and bot_route == RouteSeries:
            return BranchDecision.TOP

        # All other cases, return top branch.
        else:
            return BranchDecision.TOP


class FancyVirus(VirusType): #TODO
    CALC_STR = "7 3 + 8 - 2 * 2 /"

    def select_branch(self, top_branch: Route, bottom_branch: Route) -> BranchDecision:
        """
        Selects the branch based on the evaluated threshold from the RPN expression and compares it against
        the hacked values of computers on each branch.
        """
        #I have written this code, it has the right logic but it has a bug, I'm trying to figure it out
        # Direct evaluation of the RPN expression
        tokens = self.CALC_STR.split()
        #I also used stack, just don't forget to import stack file on your code:)
        Stack = []
        for token in tokens:
            if token.isdigit():
                Stack.append(float(token))
            else:
                b = Stack.pop()
                a = Stack.pop()
                if token == '+':
                    Stack.append(a + b)
                elif token == '-':
                    Stack.append(a - b)
                elif token == '*':
                    Stack.append(a * b)
                elif token == '/':
                    Stack.append(a / b)

        threshold = Stack.pop()  # Result of the RPN calculation
        #check wheather both routes contain computer 
        top_route = type(top_branch.store) == RouteSeries
        bot_route = type(bottom_branch.store) == RouteSeries
        if top_route and bot_route:
            if top_branch.store.computer.hacked_value < threshold:
                return BranchDecision.TOP
            if bottom_branch.store.computer.hacked_value > threshold:
                return BranchDecision.BOTTOM
            else:
                BranchDecision.STOP

        elif top_route and not bot_route:
            return BranchDecision.BOTTOM
        elif not top_route and bot_route:
            return BranchDecision.TOP
        else:
            return BranchDecision.TOP