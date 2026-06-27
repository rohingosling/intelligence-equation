#-----------------------------------------------------------------------------------------------------------------------
# Module:  board.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines the immutable nine-cell Tic-tac-toe board.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Iterator
from dataclasses     import dataclass

from domain.action import Action
from domain.mark   import Mark
from errors        import IllegalActionError, InvalidGameStateError


CELL_COUNT  = 9
EMPTY_CELLS = ( Mark.EMPTY, ) * CELL_COUNT


#-----------------------------------------------------------------------------------------------------------------------
# Class: Board
#
# Description:
#
#   An immutable Tic-tac-toe board containing exactly nine marks in canonical row-major order.
#
# Attributes:
#
#   cells : Nine immutable marks in canonical row-major order.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class Board:

    cells: tuple [ Mark, ... ] = EMPTY_CELLS

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the immutable board representation after construction.
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

        # Validate the immutable board representation after construction.

        if not isinstance ( self.cells, tuple ):
            raise InvalidGameStateError ( "Board cells must be stored in an immutable tuple." )

        if len ( self.cells ) != CELL_COUNT:
            raise InvalidGameStateError ( "A Tic-tac-toe board must contain exactly nine cells." )

        if any ( not isinstance ( mark, Mark ) for mark in self.cells ):
            raise InvalidGameStateError ( "Every board cell must contain a Mark value." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: empty
    #
    # Description:
    #
    #   Create an empty Tic-tac-toe board.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An immutable board containing nine empty cells.
    #-------------------------------------------------------------------------------------------------------------------

    @classmethod
    def empty ( cls ) -> "Board":

        # Create an empty Tic-tac-toe board.

        # Return data to caller.

        return cls ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: mark_at
    #
    # Description:
    #
    #   Return the mark at a board coordinate.
    #
    # Arguments:
    #
    #   action : Coordinate of the requested board cell.
    #
    # Returns:
    #
    #   The mark occupying the requested cell.
    #-------------------------------------------------------------------------------------------------------------------

    def mark_at ( self, action: Action ) -> Mark:

        # Return the mark at a board coordinate.

        if not isinstance ( action, Action ):
            raise TypeError ( "Board access requires an Action coordinate." )

        # Return data to caller.

        return self.cells [ self._index ( action ) ]

    #-------------------------------------------------------------------------------------------------------------------
    # Function: count
    #
    # Description:
    #
    #   Count the number of cells containing a specified mark.
    #
    # Arguments:
    #
    #   mark : Mark to count.
    #
    # Returns:
    #
    #   The number of matching cells.
    #-------------------------------------------------------------------------------------------------------------------

    def count ( self, mark: Mark ) -> int:

        # Count the number of cells containing a specified mark.

        if not isinstance ( mark, Mark ):
            raise TypeError ( "Board counts require a Mark value." )

        # Return data to caller.

        return self.cells.count ( mark )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: occupied_count
    #
    # Description:
    #
    #   Return the number of occupied cells.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   The number of cells containing X or O.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def occupied_count ( self ) -> int:

        # Return the number of occupied cells.

        # Return data to caller.

        return CELL_COUNT - self.count ( Mark.EMPTY )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: empty_count
    #
    # Description:
    #
    #   Return the number of empty cells.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   The number of cells containing Mark.EMPTY.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def empty_count ( self ) -> int:

        # Return the number of empty cells.

        # Return data to caller.

        return self.count ( Mark.EMPTY )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: place
    #
    # Description:
    #
    #   Create a successor board with one playable mark placed in an empty cell.
    #
    # Arguments:
    #
    #   action : Coordinate of the destination cell.
    #   mark   : Playable mark to place.
    #
    # Returns:
    #
    #   A new immutable board containing the placed mark.
    #-------------------------------------------------------------------------------------------------------------------

    def place ( self, action: Action, mark: Mark ) -> "Board":

        # Create a successor board with one playable mark placed in an empty cell.

        # Reject mark values outside the supported set.

        if mark not in ( Mark.X, Mark.O ):
            raise IllegalActionError ( "Only X or O may be placed on the board." )

        # Reject moves into occupied board cells.

        if self.mark_at ( action ) is not Mark.EMPTY:
            raise IllegalActionError ( f"Board coordinate {action} is already occupied." )

        # Copy the board cells before placing the next mark.

        successor_cells                            = list ( self.cells )
        successor_cells [ self._index ( action ) ] = mark

        # Return data to caller.

        return Board ( cells = tuple ( successor_cells ) )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __iter__
    #
    # Description:
    #
    #   Iterate over board marks in canonical row-major order.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An iterator over the nine board marks.
    #-------------------------------------------------------------------------------------------------------------------

    def __iter__ ( self ) -> Iterator [ Mark ]:

        # Iterate over board marks in canonical row-major order.

        # Return data to caller.

        return iter ( self.cells )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _index
    #
    # Description:
    #
    #   Convert an action coordinate to its canonical row-major tuple index.
    #
    # Arguments:
    #
    #   action : Coordinate to convert.
    #
    # Returns:
    #
    #   The corresponding tuple index from 0 through 8.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _index ( action: Action ) -> int:

        # Convert an action coordinate to its canonical row-major tuple index.

        # Return data to caller.

        return action.row * 3 + action.column
