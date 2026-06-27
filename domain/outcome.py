#-----------------------------------------------------------------------------------------------------------------------
# Module:  outcome.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines immutable game outcomes and completed winning lines.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Iterator
from dataclasses     import dataclass
from enum            import Enum

from domain.action import Action
from domain.mark   import Mark
from errors        import InvalidGameStateError


#-----------------------------------------------------------------------------------------------------------------------
# Class: OutcomeStatus
#
# Description:
#
#   The lifecycle status of a Tic-tac-toe game.
#-----------------------------------------------------------------------------------------------------------------------

class OutcomeStatus ( Enum ):

    ONGOING = "ongoing"
    DRAW    = "draw"
    WIN     = "win"


#-----------------------------------------------------------------------------------------------------------------------
# Class: WinningLine
#
# Description:
#
#   An immutable three-cell winning line.
#
# Attributes:
#
#   actions : Three distinct board coordinates in canonical line order.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class WinningLine:

    actions: tuple [ Action, Action, Action ]

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the immutable winning-line representation.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __post_init__ ( self ) -> None:

        # Validate the immutable winning-line representation.

        # Require each winning line to contain exactly three actions.

        if not isinstance ( self.actions, tuple ) or len ( self.actions ) != 3:
            raise InvalidGameStateError ( "A winning line must contain exactly three immutable actions." )

        # Reject winning lines containing non-action entries.

        if any ( not isinstance ( action, Action ) for action in self.actions ):
            raise InvalidGameStateError ( "Every winning-line cell must be an Action coordinate." )

        # Detect when len ( set ( actions ) ) differs from the expected value.

        if len ( set ( self.actions ) ) != 3:
            raise InvalidGameStateError ( "A winning line must contain three distinct cells." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __iter__
    #
    # Description:
    #
    #   Iterate over the three winning coordinates.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An iterator over the winning coordinates.
    #-------------------------------------------------------------------------------------------------------------------

    def __iter__ ( self ) -> Iterator [ Action ]:

        # Iterate over the three winning coordinates.

        # Return data to caller.

        return iter ( self.actions )


#-----------------------------------------------------------------------------------------------------------------------
# Class: Outcome
#
# Description:
#
#   An immutable Tic-tac-toe outcome with canonical winning-line details when the game is won.
#
# Attributes:
#
#   status        : Ongoing, draw, or win lifecycle status.
#   winner        : Winning playable mark, or None when the game is not won.
#   winning_lines : Every completed line belonging to the winner.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class Outcome:

    status:        OutcomeStatus
    winner:        Mark | None                = None
    winning_lines: tuple [ WinningLine, ... ] = ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate consistency between outcome status, winner, and winning lines.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __post_init__ ( self ) -> None:

        # Validate consistency between outcome status, winner, and winning lines.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.status, OutcomeStatus ):
            raise InvalidGameStateError ( "Outcome status must be an OutcomeStatus value." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.winning_lines, tuple ):
            raise InvalidGameStateError ( "Winning lines must be stored in an immutable tuple." )

        # Reject outcomes containing invalid winning-line entries.

        if any ( not isinstance ( winning_line, WinningLine ) for winning_line in self.winning_lines ):
            raise InvalidGameStateError ( "Every winning line must be a WinningLine value." )

        # Require a winner and at least one winning line for won outcomes.

        if self.status is OutcomeStatus.WIN:
            if self.winner not in ( Mark.X, Mark.O ) or not self.winning_lines:
                raise InvalidGameStateError ( "A winning outcome requires a playable winner and at least one line." )
        elif self.winner is not None or self.winning_lines:
            raise InvalidGameStateError ( "Only a winning outcome may contain a winner or winning lines." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: ongoing
    #
    # Description:
    #
    #   Create an ongoing game outcome.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An immutable ongoing outcome.
    #-------------------------------------------------------------------------------------------------------------------

    @classmethod
    def ongoing ( cls ) -> "Outcome":

        # Create an ongoing game outcome.

        # Return data to caller.

        return cls ( status = OutcomeStatus.ONGOING )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: draw
    #
    # Description:
    #
    #   Create a drawn game outcome.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An immutable draw outcome.
    #-------------------------------------------------------------------------------------------------------------------

    @classmethod
    def draw ( cls ) -> "Outcome":

        # Create a drawn game outcome.

        # Return data to caller.

        return cls ( status = OutcomeStatus.DRAW )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: win
    #
    # Description:
    #
    #   Create a winning game outcome.
    #
    # Arguments:
    #
    #   winner        : Playable mark that won the game.
    #   winning_lines : Every completed line belonging to the winner.
    #
    # Returns:
    #
    #   An immutable winning outcome.
    #-------------------------------------------------------------------------------------------------------------------

    @classmethod
    def win ( cls, winner: Mark, winning_lines: tuple [ WinningLine, ... ] ) -> "Outcome":

        # Create a winning game outcome.

        # Return data to caller.

        return cls (
            status        = OutcomeStatus.WIN,
            winner        = winner,
            winning_lines = winning_lines,
        )
