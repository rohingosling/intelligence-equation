#-----------------------------------------------------------------------------------------------------------------------
# Module:  human_player.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements a runtime human player over an injected coordinate-input and diagnostic-output port.
#
#-----------------------------------------------------------------------------------------------------------------------

from typing import Protocol, runtime_checkable

from domain.action     import Action
from domain.game_rules import GameRules
from domain.game_state import GameState
from domain.mark       import Mark
from domain.player     import PlayerDecision, PlayerProfile, PlayerType
from errors            import CoordinateError, IllegalActionError


#-----------------------------------------------------------------------------------------------------------------------
# Class: HumanInput
#
# Description:
#
#   Structural terminal-input contract consumed by HumanPlayer.
#-----------------------------------------------------------------------------------------------------------------------

@runtime_checkable
class HumanInput ( Protocol ):

    #-------------------------------------------------------------------------------------------------------------------
    # Function: request_coordinate
    #
    # Description:
    #
    #   Request one coordinate from the human input boundary.
    #
    # Arguments:
    #
    #   player_name : Player name supplied to the operation.
    #
    # Returns:
    #
    #   Coordinate text supplied by the human input boundary.
    #-------------------------------------------------------------------------------------------------------------------

    def request_coordinate ( self, player_name: str ) -> str:

        # Request one coordinate from the human input boundary.

        ...

    #-------------------------------------------------------------------------------------------------------------------
    # Function: show_input_error
    #
    # Description:
    #
    #   Display one recoverable input error to the human player.
    #
    # Arguments:
    #
    #   message : Human-readable validation or runtime message.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def show_input_error ( self, message: str ) -> None:

        # Display one recoverable input error to the human player.

        ...


#-----------------------------------------------------------------------------------------------------------------------
# Class: HumanPlayer
#
# Description:
#
#   Repeatedly request and validate human coordinates without applying game transitions.
#-----------------------------------------------------------------------------------------------------------------------

class HumanPlayer:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   profile     : Validated player profile.
    #   mark        : Player mark assigned to the runtime player or board cell.
    #   game_rules  : Authoritative Tic-tac-toe rule service.
    #   human_input : Human input supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        profile: PlayerProfile,
        mark: Mark,
        game_rules: GameRules,
        human_input: HumanInput,
    ) -> None:

        # Validate the runtime player identity and dependencies.

        if not isinstance ( profile, PlayerProfile ) or profile.player_type is not PlayerType.HUMAN:
            raise TypeError ( "HumanPlayer requires a human PlayerProfile." )

        # Reject mark values outside the supported set.

        if mark not in ( Mark.X, Mark.O ):
            raise ValueError ( "HumanPlayer requires an assigned X or O mark." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "HumanPlayer requires a GameRules service." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( human_input, HumanInput ):
            raise TypeError ( "HumanPlayer requires a HumanInput port." )

        # Store the validated human player dependencies.

        self.profile     = profile
        self.mark        = mark
        self.game_rules  = game_rules
        self.human_input = human_input

    #-------------------------------------------------------------------------------------------------------------------
    # Function: choose_action
    #
    # Description:
    #
    #   Prompt until one well-formed legal coordinate is entered.
    #
    # Arguments:
    #
    #   state : Current immutable game state.
    #
    # Returns:
    #
    #   Player decision containing the selected action.
    #-------------------------------------------------------------------------------------------------------------------

    def choose_action ( self, state: GameState ) -> PlayerDecision:

        # Validate that this runtime player owns the current ongoing turn.

        if not isinstance ( state, GameState ):
            raise IllegalActionError ( "Human players require an immutable GameState." )

        # Validate the supplied game state before selecting an action.

        self.game_rules.validate_state ( state )

        # Reject moves or decisions after the game has already ended.

        if state.is_terminal:
            raise IllegalActionError ( "Human players cannot choose an action from a terminal state." )

        # Reject decisions requested for the wrong player's turn.

        if self.game_rules.player_to_move ( state ) is not self.mark:
            raise IllegalActionError ( "Human player mark does not match the state player to move." )

        legal_actions = self.game_rules.legal_actions ( state )

        # Recover from malformed and occupied coordinates without changing the supplied state.

        while True:

            # Read the next human coordinate from the input service.

            coordinate_text = self.human_input.request_coordinate ( self.profile.name )

            # Parse the coordinate and let the player retry malformed input.

            try:
                action = Action.parse ( coordinate_text )
            except CoordinateError as error:
                self.human_input.show_input_error ( str ( error ) )
                continue

            # Reject human input that names an occupied or illegal cell.

            if action not in legal_actions:
                self.human_input.show_input_error ( f"Board coordinate {action} is already occupied." )
                continue

            # Return data to caller.

            return PlayerDecision (
                action      = action,
                diagnostics = ( "source", "human_input" ),
            )
