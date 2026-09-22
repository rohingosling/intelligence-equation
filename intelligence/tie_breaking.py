#-----------------------------------------------------------------------------------------------------------------------
# Module:  tie_breaking.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Provides validated deterministic and seeded-random selection among equally scored actions.
#
#-----------------------------------------------------------------------------------------------------------------------

from enum   import Enum
from random import Random

from domain.action import Action


#-----------------------------------------------------------------------------------------------------------------------
# Class: TieBreaker
#
# Description:
#
#   Identifies the supported policies for selecting among equally scored actions.
#-----------------------------------------------------------------------------------------------------------------------

class TieBreaker ( Enum ):

    DETERMINISTIC = "deterministic"
    RANDOM        = "random"


#-----------------------------------------------------------------------------------------------------------------------
# Function: parse_tie_breaker
#
# Description:
#
#   Convert configuration text or an existing enumeration value into a validated tie-breaker policy.
#
# Arguments:
#
#   value   : Value supplied by the caller.
#   default : Default supplied to the operation.
#
# Returns:
#
#   Normalized tie-breaker enumeration value.
#-----------------------------------------------------------------------------------------------------------------------

def parse_tie_breaker (
    value: object,
    default: TieBreaker = TieBreaker.DETERMINISTIC,
) -> TieBreaker:

    # Normalize the optional policy value.

    # Use the default policy when no tie-breaker value is configured.

    if value is None:

        # Return data to caller.

        return default

    # Handle values where value has the expected TieBreaker shape.

    if isinstance ( value, TieBreaker ):

        # Return data to caller.

        return value

    # Handle values where value has the expected str shape.

    if isinstance ( value, str ):

        # Normalize the configured tie-breaker value.

        normalized_value = value.strip ().lower ()

        # Search the tie-breaker enum for the configured value.

        for tie_breaker in TieBreaker:
            if tie_breaker.value == normalized_value:

                # Return data to caller.

                return tie_breaker

    # Raise the domain error for the invalid input.

    raise ValueError ( "Tie breaker must be 'deterministic' or 'random'." )


#-----------------------------------------------------------------------------------------------------------------------
# Function: select_tied_action
#
# Description:
#
#   Select one action from a non-empty tied set using canonical or seeded-random behavior.
#
# Arguments:
#
#   actions          : Candidate actions available for tie breaking.
#   tie_breaker      : Tie-breaking policy used when scores are equal.
#   random_generator : Shared random-number generator for stochastic choices.
#
# Returns:
#
#   Selected action from the tied candidate group.
#-----------------------------------------------------------------------------------------------------------------------

def select_tied_action (
    actions: tuple [ Action, ... ],
    tie_breaker: TieBreaker,
    random_generator: Random,
) -> Action:

    # Validate the tied candidate set and selection dependencies.

    if not isinstance ( actions, tuple ) or not actions:
        raise ValueError ( "Tie-breaking requires a non-empty immutable action tuple." )

    # Reject action collections containing non-action entries.

    if any ( not isinstance ( action, Action ) for action in actions ):
        raise TypeError ( "Tie-breaking candidates must be Action values." )

    # Detect when len ( actions ) differs from the expected value.

    if len ( actions ) != len ( set ( actions ) ):
        raise ValueError ( "Tie-breaking candidates must be unique." )

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( tie_breaker, TieBreaker ):
        raise TypeError ( "Tie-breaking requires a TieBreaker value." )

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( random_generator, Random ):
        raise TypeError ( "Tie-breaking requires an injected random-number generator." )

    # Use coordinate order for deterministic tie-breaking.

    if tie_breaker is TieBreaker.DETERMINISTIC:

        # Return data to caller.

        return min ( actions )

    # Return data to caller.

    return random_generator.choice ( actions )
