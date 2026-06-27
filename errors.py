#-----------------------------------------------------------------------------------------------------------------------
# Module:  errors.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines shared exception types used at application and architectural boundaries.
#
#-----------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------
# Class: ApplicationError
#
# Description:
#
#   Base class for expected application failures.
#-----------------------------------------------------------------------------------------------------------------------

class ApplicationError ( Exception ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: ConfigurationError
#
# Description:
#
#   Raised when configuration cannot be read, parsed, or validated.
#-----------------------------------------------------------------------------------------------------------------------

class ConfigurationError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: CoordinateError
#
# Description:
#
#   Raised when a human coordinate is malformed or outside the board.
#-----------------------------------------------------------------------------------------------------------------------

class CoordinateError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: IllegalActionError
#
# Description:
#
#   Raised when an action is not legal for the current game state.
#-----------------------------------------------------------------------------------------------------------------------

class IllegalActionError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: InvalidGameStateError
#
# Description:
#
#   Raised when a board, outcome, or state violates a Tic-tac-toe invariant.
#-----------------------------------------------------------------------------------------------------------------------

class InvalidGameStateError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: TerminalStateError
#
# Description:
#
#   Raised when a transition is requested from a terminal state.
#-----------------------------------------------------------------------------------------------------------------------

class TerminalStateError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: StrategyContractError
#
# Description:
#
#   Raised when an intelligence strategy violates its selection contract.
#-----------------------------------------------------------------------------------------------------------------------

class StrategyContractError ( ApplicationError ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Class: InputEndedError
#
# Description:
#
#   Raised when terminal input ends before a human turn is completed.
#-----------------------------------------------------------------------------------------------------------------------

class InputEndedError ( ApplicationError ):

    pass
