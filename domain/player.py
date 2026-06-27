#-----------------------------------------------------------------------------------------------------------------------
# Module:  player.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines immutable player identity and decision values together with the runtime player protocol.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from dataclasses     import dataclass, field
from enum            import Enum
from types           import MappingProxyType
from typing          import Protocol, runtime_checkable

from domain.action     import Action
from domain.game_state import GameState
from domain.mark       import Mark


#-----------------------------------------------------------------------------------------------------------------------
# Class: PlayerType
#
# Description:
#
#   Identifies whether a player is controlled by a human or a computer intelligence system.
#-----------------------------------------------------------------------------------------------------------------------

class PlayerType ( Enum ):

    HUMAN    = "human"
    COMPUTER = "computer"


#-----------------------------------------------------------------------------------------------------------------------
# Class: PlayerProfile
#
# Description:
#
#   An immutable configured player identity used to construct one or more runtime players.
#
# Attributes:
#
#   profile_id              : Unique configuration identifier.
#   name                    : User-facing player name.
#   player_type             : Human or computer control type.
#   intelligence_type       : Computer intelligence-system identifier, or None for a human.
#   intelligence_parameters : Immutable intelligence-system parameters.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class PlayerProfile:

    profile_id:              str
    name:                    str
    player_type:             PlayerType
    intelligence_type:       str | None              = None
    intelligence_parameters: Mapping [ str, object ] = field ( default_factory = dict )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate and normalize the immutable player profile.
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

        #-----------------------------------------
        # Validate the configured player identity.
        #-----------------------------------------

        # Reject player profiles without a non-empty identifier.

        if not isinstance ( self.profile_id, str ) or not self.profile_id.strip ():
            raise ValueError ( "Player profile identifiers must be non-empty text." )

        # Reject player profiles without a non-empty display name.

        if not isinstance ( self.name, str ) or not self.name.strip ():
            raise ValueError ( "Player names must be non-empty text." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.player_type, PlayerType ):
            raise TypeError ( "Player type must be a PlayerType value." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.intelligence_parameters, Mapping ):
            raise TypeError ( "Intelligence parameters must be a mapping." )

        # Reject mappings whose keys are not text values.

        if any (
            not isinstance ( parameter_name, str ) or not parameter_name.strip ()
            for parameter_name in self.intelligence_parameters
        ):
            raise ValueError ( "Intelligence parameter names must be non-empty text." )

        #--------------------------------------------------
        # Validate the profile schema for its control type.
        #--------------------------------------------------

        # Apply the profile rules that differ between human and computer players.

        if self.player_type is PlayerType.HUMAN:
            if self.intelligence_type is not None or self.intelligence_parameters:
                raise ValueError ( "Human player profiles cannot contain intelligence settings." )
        elif not isinstance ( self.intelligence_type, str ) or not self.intelligence_type.strip ():
            raise ValueError ( "Computer player profiles require an intelligence type." )

        # Normalize strings and copy strategy parameters into a read-only mapping.

        normalized_intelligence_type = (
            self.intelligence_type.strip ()
            if isinstance ( self.intelligence_type, str )
            else None
        )

        # Normalize immutable profile text fields after validation.

        object.__setattr__ ( self, "profile_id", self.profile_id.strip () )
        object.__setattr__ ( self, "name", self.name.strip () )
        object.__setattr__ ( self, "intelligence_type", normalized_intelligence_type )
        object.__setattr__ (
            self,
            "intelligence_parameters",
            MappingProxyType ( dict ( self.intelligence_parameters ) ),
        )


#-----------------------------------------------------------------------------------------------------------------------
# Class: PlayerDecision
#
# Description:
#
#   An immutable action selected by a runtime player with optional structured diagnostics.
#
# Attributes:
#
#   action      : Selected board coordinate.
#   diagnostics : Optional strategy or input diagnostics retained with match history.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class PlayerDecision:

    action:      Action
    diagnostics: object | None = None

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the selected action.
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

        # Validate the selected action.

        if not isinstance ( self.action, Action ):
            raise TypeError ( "A player decision requires an Action." )


#-----------------------------------------------------------------------------------------------------------------------
# Class: Player
#
# Description:
#
#   Structural contract implemented by every runtime human or computer participant.
#
# Attributes:
#
#   profile : Profile.
#   mark    : Mark.
#-----------------------------------------------------------------------------------------------------------------------

@runtime_checkable
class Player ( Protocol ):

    profile: PlayerProfile
    mark:    Mark

    #-------------------------------------------------------------------------------------------------------------------
    # Function: choose_action
    #
    # Description:
    #
    #   Select one action for the supplied immutable game state.
    #
    # Arguments:
    #
    #   state : Current ongoing game state.
    #
    # Returns:
    #
    #   The selected action and optional diagnostics.
    #-------------------------------------------------------------------------------------------------------------------

    def choose_action ( self, state: GameState ) -> PlayerDecision:

        # Choose one legal action for the current game state.

        ...
