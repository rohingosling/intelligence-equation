#-----------------------------------------------------------------------------------------------------------------------
# Module:  minimax_strategy.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements complete memoized minimax search through the authoritative immutable game transitions.
#
#-----------------------------------------------------------------------------------------------------------------------

from functools import lru_cache
from random    import Random

from domain.action                      import Action
from domain.game_rules                  import GameRules
from domain.game_state                  import GameState
from domain.mark                        import Mark
from intelligence.intelligence_strategy import ActionScore, StrategyDecision, validate_strategy_request
from intelligence.tie_breaking          import TieBreaker, parse_tie_breaker, select_tied_action


#-----------------------------------------------------------------------------------------------------------------------
# Class: MinimaxStrategy
#
# Description:
#
#   Searches the complete remaining game tree and selects an optimal action from the acting player's perspective.
#-----------------------------------------------------------------------------------------------------------------------

class MinimaxStrategy:

    NAME = "minimax"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   game_rules  : Authoritative Tic-tac-toe rule service.
    #   tie_breaker : Tie-breaking policy used when scores are equal.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        game_rules: GameRules,
        tie_breaker: TieBreaker | str = TieBreaker.DETERMINISTIC,
    ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "MinimaxStrategy requires a GameRules service." )

        # Store the validated strategy dependencies.

        self.game_rules  = game_rules
        self.tie_breaker = parse_tie_breaker ( tie_breaker )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: name
    #
    # Description:
    #
    #   Return the public strategy name.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Public strategy name.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def name ( self ) -> str:

        # Return data to caller.

        return self.NAME

    #-------------------------------------------------------------------------------------------------------------------
    # Function: select_action
    #
    # Description:
    #
    #   Select one legal action according to the strategy contract.
    #
    # Arguments:
    #
    #   state            : Current immutable game state.
    #   acting_mark      : Mark assigned to the strategy for the current decision.
    #   legal_actions    : Canonical legal actions available in the current state.
    #   random_generator : Shared random-number generator for stochastic choices.
    #
    # Returns:
    #
    #   Strategy decision with the selected action, action scores, and metadata.
    #-------------------------------------------------------------------------------------------------------------------

    def select_action (
        self,
        state: GameState,
        acting_mark: Mark,
        legal_actions: tuple [ Action, ... ],
        random_generator: Random,
    ) -> StrategyDecision:

        # Validate the common strategy contract.

        validate_strategy_request (
            game_rules       = self.game_rules,
            state            = state,
            acting_mark      = acting_mark,
            legal_actions    = legal_actions,
            random_generator = random_generator,
        )

        # Capture minimax cache statistics before evaluating the move.

        cache_before = self._evaluate_state.cache_info ()
        action_scores = tuple (
            ActionScore (
                action = action,
                score = self._evaluate_state (
                    self.game_rules.apply_action ( state, action ),
                    acting_mark,
                ),
            )
            for action in legal_actions
        )

        # Capture minimax cache statistics after evaluating the move.

        cache_after = self._evaluate_state.cache_info ()
        best_score  = max ( action_score.score for action_score in action_scores )

        best_actions = tuple (
            action_score.action
            for action_score in action_scores
            if action_score.score == best_score
        )

        # Select among tied best actions using the configured tie-breaker.

        selected_action = select_tied_action (
            actions          = best_actions,
            tie_breaker      = self.tie_breaker,
            random_generator = random_generator,
        )

        # Return data to caller.

        return StrategyDecision (
            action        = selected_action,
            strategy_name = self.name,
            action_scores = action_scores,
            metadata = {
                "tie_breaker": self.tie_breaker.value,
                "evaluated_state_count": cache_after.misses - cache_before.misses,
                "cache_hits": cache_after.hits - cache_before.hits,
            },
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _evaluate_state
    #
    # Description:
    #
    #   Evaluate state.
    #
    # Arguments:
    #
    #   state       : Current immutable game state.
    #   perspective : Perspective supplied to the operation.
    #
    # Returns:
    #
    #   Integer value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @lru_cache ( maxsize = None )
    def _evaluate_state ( self, state: GameState, perspective: Mark ) -> int:

        # Return terminal utility at the leaves of the complete game tree.

        if state.is_terminal:

            # Return data to caller.

            return self.game_rules.utility ( state, perspective )

        # Evaluate every successor and maximize or minimize according to the player to move.

        successor_values = tuple (
            self._evaluate_state (
                self.game_rules.apply_action ( state, action ),
                perspective,
            )
            for action in self.game_rules.legal_actions ( state )
        )

        # Maximize the score when the perspective mark is to move.

        if self.game_rules.player_to_move ( state ) is perspective:

            # Return data to caller.

            return max ( successor_values )

        # Return data to caller.

        return min ( successor_values )
