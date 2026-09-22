#-----------------------------------------------------------------------------------------------------------------------
# Module:  mark.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines the marks that may occupy a Tic-tac-toe board cell.
#
#-----------------------------------------------------------------------------------------------------------------------

from enum import Enum


#-----------------------------------------------------------------------------------------------------------------------
# Class: Mark
#
# Description:
#
#   A mark that may occupy a Tic-tac-toe board cell.
#-----------------------------------------------------------------------------------------------------------------------

class Mark ( Enum ):

    EMPTY = ""
    X     = "X"
    O     = "O"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: opponent
    #
    # Description:
    #
    #   Return the opposing playable mark.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Mark.O for Mark.X, or Mark.X for Mark.O.
    #-------------------------------------------------------------------------------------------------------------------

    def opponent ( self ) -> "Mark":

        # Return the opposing playable mark.

        # Return O as the opponent of X.

        if self is Mark.X:

            # Return data to caller.

            return Mark.O

        # Return X as the opponent of O.

        if self is Mark.O:

            # Return data to caller.

            return Mark.X

        # Raise the domain error for the invalid input.

        raise ValueError ( "The empty mark has no opponent." )
