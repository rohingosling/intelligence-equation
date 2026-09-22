#-----------------------------------------------------------------------------------------------------------------------
# Module:  game.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements complete match orchestration over abstract runtime players and immutable game history.
#
#-----------------------------------------------------------------------------------------------------------------------

from typing import Protocol, runtime_checkable

from domain.action     import Action
from domain.game_rules import GameRules
from domain.game_state import GameState
from domain.history    import GameHistory, MatchResult, MoveRecord
from domain.mark       import Mark
from domain.player     import Player, PlayerDecision
from errors            import InvalidGameStateError, StrategyContractError


#-----------------------------------------------------------------------------------------------------------------------
# Class: GameObserver
#
# Description:
#
#   Receives ordered match lifecycle events without introducing presentation concerns into the game engine.
#-----------------------------------------------------------------------------------------------------------------------

@runtime_checkable
class GameObserver ( Protocol ):

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_game_started
    #
    # Description:
    #
    #   Handle the ordered match-start lifecycle event.
    #
    # Arguments:
    #
    #   state   : Current immutable game state.
    #   players : Runtime players participating in the match.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def on_game_started ( self, state: GameState, players: tuple [ Player, Player ] ) -> None:

        # Handle the ordered match-start lifecycle event.

        ...

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_move_completed
    #
    # Description:
    #
    #   Handle one accepted-move lifecycle event.
    #
    # Arguments:
    #
    #   record : Accepted move record to render or publish.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def on_move_completed ( self, record: MoveRecord ) -> None:

        # Handle one accepted-move lifecycle event.

        ...

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_game_completed
    #
    # Description:
    #
    #   Handle the ordered match-completed lifecycle event.
    #
    # Arguments:
    #
    #   result : Completed match result.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def on_game_completed ( self, result: MatchResult ) -> None:

        # Handle the ordered match-completed lifecycle event.

        ...


#-----------------------------------------------------------------------------------------------------------------------
# Class: Game
#
# Description:
#
#   Coordinates one complete match through the authoritative game rules and abstract player protocol.
#-----------------------------------------------------------------------------------------------------------------------

class Game:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the match engine with shared rules and an optional lifecycle observer.
    #
    # Arguments:
    #
    #   game_rules : Authoritative game-rule service.
    #   observer   : Optional receiver for ordered lifecycle events.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, game_rules: GameRules, observer: GameObserver | None = None ) -> None:

        # Validate and retain match dependencies.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "Game requires a GameRules service." )

        # Reject observers that do not satisfy the game observer protocol.

        if observer is not None and not isinstance ( observer, GameObserver ):
            raise TypeError ( "Game observer does not implement the GameObserver protocol." )

        self.game_rules = game_rules
        self.observer   = observer

    #-------------------------------------------------------------------------------------------------------------------
    # Function: play
    #
    # Description:
    #
    #   Run one complete match and return its immutable result.
    #
    # Arguments:
    #
    #   player_x : Runtime player assigned to X.
    #   player_o : Runtime player assigned to O.
    #
    # Returns:
    #
    #   The completed match result and accepted-move history.
    #-------------------------------------------------------------------------------------------------------------------

    def play ( self, player_x: Player, player_o: Player ) -> MatchResult:

        # Validate the runtime participants before publishing match events.

        self._validate_players ( player_x, player_o )

        players = ( player_x, player_o )
        state   = self.game_rules.initial_state ()
        history = GameHistory ()

        self._publish_game_started ( state, players )

        # Request, validate, apply, and record decisions until the state is terminal.

        while not state.is_terminal:

            current_mark   = self.game_rules.player_to_move ( state )
            current_player = player_x if current_mark is Mark.X else player_o
            legal_actions  = self.game_rules.legal_actions ( state )
            decision       = current_player.choose_action ( state )

            # Validate the player decision before applying it to the game state.

            self._validate_decision ( decision, legal_actions, current_player )

            # Advance the game state and record the completed move.

            state = self.game_rules.apply_action ( state, decision.action )
            record = MoveRecord (
                move_number       = state.move_number,
                player_profile_id = current_player.profile.profile_id,
                player_name       = current_player.profile.name,
                player_type       = current_player.profile.player_type,
                mark              = current_player.mark,
                action            = decision.action,
                state_after       = state,
                decision          = decision,
            )
            history = history.append ( record )

            self._publish_move_completed ( record )

        # Build and publish the completed immutable result.

        result = MatchResult (
            player_1    = player_x,
            player_2    = player_o,
            final_state = state,
            outcome     = state.outcome,
            history     = history,
        )

        self._publish_game_completed ( result )

        # Return data to caller.

        return result

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_players
    #
    # Description:
    #
    #   Validate runtime player contracts and mark assignments.
    #
    # Arguments:
    #
    #   player_x : Candidate player for X.
    #   player_o : Candidate player for O.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _validate_players ( player_x: Player, player_o: Player ) -> None:

        # Validate structural player contracts.

        # Reject match participants that are not Player objects.

        if not isinstance ( player_x, Player ) or not isinstance ( player_o, Player ):
            raise TypeError ( "Game requires two objects implementing the Player protocol." )

        # Reject using the same player object for both sides.

        if player_x is player_o:
            raise InvalidGameStateError ( "The two match slots require separate runtime player objects." )

        # Require the supplied players to own the X and O marks respectively.

        if player_x.mark is not Mark.X or player_o.mark is not Mark.O:
            raise InvalidGameStateError ( "Player 1 must use X and Player 2 must use O." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_decision
    #
    # Description:
    #
    #   Enforce the player action-selection contract at the game boundary.
    #
    # Arguments:
    #
    #   decision       : Value returned by the current player.
    #   legal_actions  : Canonical legal actions for the current state.
    #   current_player : Runtime player that returned the decision.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _validate_decision (
        decision: PlayerDecision,
        legal_actions: tuple [ Action, ... ],
        current_player: Player,
    ) -> None:

        # Validate the decision value and selected action.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( decision, PlayerDecision ):
            raise StrategyContractError (
                f"Player {current_player.profile.name} did not return a PlayerDecision."
            )

        # Reject decisions that choose an illegal action.

        if decision.action not in legal_actions:
            raise StrategyContractError (
                f"Player {current_player.profile.name} selected illegal action {decision.action}."
            )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _publish_game_started
    #
    # Description:
    #
    #   Publish the initial-state event when an observer is present.
    #
    # Arguments:
    #
    #   state   : Current immutable game state.
    #   players : Runtime players participating in the match.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _publish_game_started ( self, state: GameState, players: tuple [ Player, Player ] ) -> None:

        # Publish game started.

        if self.observer is not None:
            self.observer.on_game_started ( state, players )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _publish_move_completed
    #
    # Description:
    #
    #   Publish one accepted-move event when an observer is present.
    #
    # Arguments:
    #
    #   record : Accepted move record to render or publish.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _publish_move_completed ( self, record: MoveRecord ) -> None:

        # Publish move completed.

        if self.observer is not None:
            self.observer.on_move_completed ( record )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _publish_game_completed
    #
    # Description:
    #
    #   Publish the completed-match event when an observer is present.
    #
    # Arguments:
    #
    #   result : Completed match result.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _publish_game_completed ( self, result: MatchResult ) -> None:

        # Publish game completed.

        if self.observer is not None:
            self.observer.on_game_completed ( result )
