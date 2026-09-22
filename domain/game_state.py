#-----------------------------------------------------------------------------------------------------------------------
# Module:  game_state.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines an immutable Tic-tac-toe game-state snapshot.
#
#-----------------------------------------------------------------------------------------------------------------------

from dataclasses import dataclass

from domain.board   import Board
from domain.outcome import Outcome, OutcomeStatus
from errors         import InvalidGameStateError


#-----------------------------------------------------------------------------------------------------------------------
# Class: GameState
#
# Description:
#
#   An immutable board, accepted-move count, and derived outcome snapshot.
#
# Attributes:
#
#   board       : Immutable board position.
#   move_number : Number of accepted moves represented by the board.
#   outcome     : Derived lifecycle outcome for the board.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class GameState:

    board:       Board
    move_number: int
    outcome:     Outcome

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the structural consistency of the immutable state snapshot.
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

        # Validate the structural consistency of the immutable state snapshot.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.board, Board ):
            raise InvalidGameStateError ( "A game state requires an immutable Board." )

        # Reject values that do not satisfy the required type or range.

        if type ( self.move_number ) is not int or not 0 <= self.move_number <= 9:
            raise InvalidGameStateError ( "Move number must be an integer from 0 through 9." )

        # Detect when move number differs from the expected value.

        if self.move_number != self.board.occupied_count:
            raise InvalidGameStateError ( "Move number must equal the number of occupied board cells." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.outcome, Outcome ):
            raise InvalidGameStateError ( "A game state requires an immutable Outcome." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: is_terminal
    #
    # Description:
    #
    #   Report whether the game has reached a win or draw.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   True when the state is terminal; otherwise False.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def is_terminal ( self ) -> bool:

        # Report whether the game has reached a win or draw.

        # Return data to caller.

        return self.outcome.status is not OutcomeStatus.ONGOING
