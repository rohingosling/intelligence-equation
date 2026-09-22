#-----------------------------------------------------------------------------------------------------------------------
# Module:  action.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines immutable Tic-tac-toe board coordinates and user-facing coordinate notation.
#
#-----------------------------------------------------------------------------------------------------------------------

from dataclasses import dataclass

from errors import CoordinateError


BOARD_SIZE     = 3
COLUMN_LETTERS = "abc"


#-----------------------------------------------------------------------------------------------------------------------
# Class: Action
#
# Description:
#
#   An immutable zero-based row and column coordinate on the Tic-tac-toe board.
#
# Attributes:
#
#   row    : Zero-based row index from 0 through 2.
#   column : Zero-based column index from 0 through 2.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True, order = True )
class Action:

    row:    int
    column: int

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the immutable coordinate after construction.
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

        # Validate the immutable coordinate after construction.

        if type ( self.row ) is not int or type ( self.column ) is not int:
            raise CoordinateError ( "Board row and column indices must be integers." )

        if not 0 <= self.row < BOARD_SIZE or not 0 <= self.column < BOARD_SIZE:
            raise CoordinateError ( "Board coordinates must be within the 3 by 3 board." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: parse
    #
    # Description:
    #
    #   Parse a user-facing coordinate in column-row notation.
    #
    # Arguments:
    #
    #   coordinate_text : Coordinate text such as "a1", with optional surrounding whitespace.
    #
    # Returns:
    #
    #   The parsed immutable action.
    #-------------------------------------------------------------------------------------------------------------------

    @classmethod
    def parse ( cls, coordinate_text: str ) -> "Action":

        # Parse a user-facing coordinate in column-row notation.

        if not isinstance ( coordinate_text, str ):
            raise CoordinateError ( "A board coordinate must be text in the range a1 through c3." )

        # Normalize the coordinate text before parsing it.

        normalized_coordinate = coordinate_text.strip ().lower ()

        if ( len ( normalized_coordinate ) != 2
             or normalized_coordinate [ 0 ] not in COLUMN_LETTERS
             or normalized_coordinate [ 1 ] not in "123" ):
            raise CoordinateError ( "A board coordinate must be in the range a1 through c3." )

        # Convert the column letter into a zero-based board column.

        column = COLUMN_LETTERS.index ( normalized_coordinate [ 0 ] )
        row    = int ( normalized_coordinate [ 1 ] ) - 1

        # Return data to caller.

        return cls ( row = row, column = column )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: to_notation
    #
    # Description:
    #
    #   Convert the coordinate to canonical lowercase column-row notation.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Canonical coordinate text from "a1" through "c3".
    #-------------------------------------------------------------------------------------------------------------------

    def to_notation ( self ) -> str:

        # Convert the coordinate to canonical lowercase column-row notation.

        # Return data to caller.

        return f"{COLUMN_LETTERS [ self.column ]}{self.row + 1}"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __str__
    #
    # Description:
    #
    #   Return the canonical user-facing coordinate notation.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Canonical coordinate text from "a1" through "c3".
    #-------------------------------------------------------------------------------------------------------------------

    def __str__ ( self ) -> str:

        # Return the canonical user-facing coordinate notation.

        # Return data to caller.

        return self.to_notation ()
