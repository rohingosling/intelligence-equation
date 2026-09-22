#-----------------------------------------------------------------------------------------------------------------------
# Module:  causal_entropy_strategy.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements pure causal-entropic action selection by counting uniformly weighted legal future histories.
#
#-----------------------------------------------------------------------------------------------------------------------

from dataclasses import dataclass
from math        import isclose, isfinite, log
from random      import Random

from domain.action                      import Action
from domain.board                       import Board
from domain.game_rules                  import GameRules
from domain.game_state                  import GameState
from domain.mark                        import Mark
from intelligence.intelligence_strategy import ActionScore, StrategyDecision, validate_strategy_request
from intelligence.tie_breaking          import TieBreaker, parse_tie_breaker, select_tied_action


DEFAULT_HORIZON          = 5
DEFAULT_TEMPERATURE      = 1.0
SCORE_ABSOLUTE_TOLERANCE = 1.0e-12
SCORE_RELATIVE_TOLERANCE = 1.0e-12


#-----------------------------------------------------------------------------------------------------------------------
# Class: _SearchStatistics
#
# Description:
#
#   Accumulates cache-independent diagnostic counts for one causal-entropy decision.
#
# Attributes:
#
#   evaluated_state_count : Number of uncached states evaluated for one decision.
#   cache_hits            : Number of recursive search requests served from cache.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass
class _SearchStatistics:

    evaluated_state_count: int = 0
    cache_hits:            int = 0


#-----------------------------------------------------------------------------------------------------------------------
# Class: CausalEntropyStrategy
#
# Description:
#
#   Selects actions that maximize temperature-scaled future-history entropy without game utility or tactical rules.
#-----------------------------------------------------------------------------------------------------------------------

class CausalEntropyStrategy:

    NAME = "causal_entropy"

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
    #   horizon     : Future search depth used by the causal-entropy strategy.
    #   temperature : Temperature multiplier applied to entropy differences.
    #   tie_breaker : Tie-breaking policy used when scores are equal.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        game_rules: GameRules,
        horizon: int                  = DEFAULT_HORIZON,
        temperature: int | float      = DEFAULT_TEMPERATURE,
        tie_breaker: TieBreaker | str = TieBreaker.DETERMINISTIC,
    ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "CausalEntropyStrategy requires a GameRules service." )

        # Reject causal-entropy horizons shorter than one ply.

        if type ( horizon ) is not int or horizon < 1:
            raise ValueError ( "Causal-entropy horizon must be an integer of at least 1." )

        # Handle values where temperature, bool ) or not isinstance ( temperature, ( int has the expected float ) shape.

        if isinstance ( temperature, bool ) or not isinstance ( temperature, ( int, float ) ):
            raise ValueError ( "Causal-entropy temperature must be a finite number greater than 0." )

        # Normalize the temperature parameter to a floating-point value.

        normalized_temperature = float ( temperature )

        if not isfinite ( normalized_temperature ) or normalized_temperature <= 0.0:
            raise ValueError ( "Causal-entropy temperature must be a finite number greater than 0." )

        # Store the validated strategy dependencies.

        self.game_rules  = game_rules
        self.horizon     = horizon
        self.temperature = normalized_temperature
        self.tie_breaker = parse_tie_breaker ( tie_breaker )
        self._path_count_cache: dict [ tuple [ Board, int ], int ] = {}

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
    # Function: future_history_count
    #
    # Description:
    #
    #   Count legal future histories from a state within the configured horizon.
    #
    # Arguments:
    #
    #   state           : Current immutable game state.
    #   remaining_depth : Remaining recursive search depth.
    #
    # Returns:
    #
    #   Number of legal future histories reachable within the requested depth.
    #-------------------------------------------------------------------------------------------------------------------

    def future_history_count (
        self,
        state: GameState,
        remaining_depth: int | None = None,
    ) -> int:

        # Validate the public recurrence request.

        if not isinstance ( state, GameState ):
            raise TypeError ( "Future-history counting requires an immutable GameState." )

        # Validate the supplied game state before selecting an action.

        self.game_rules.validate_state ( state )
        resolved_depth = self.horizon if remaining_depth is None else remaining_depth

        # Reject negative or non-integer search depths.

        if type ( resolved_depth ) is not int or resolved_depth < 0:
            raise ValueError ( "Future-history remaining depth must be a non-negative integer." )

        # Return data to caller.

        return self._count_future_histories ( state, resolved_depth )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: path_entropy
    #
    # Description:
    #
    #   Compute future-history entropy as the natural logarithm of the path count.
    #
    # Arguments:
    #
    #   state           : Current immutable game state.
    #   remaining_depth : Remaining recursive search depth.
    #
    # Returns:
    #
    #   Natural-log future-history entropy.
    #-------------------------------------------------------------------------------------------------------------------

    def path_entropy (
        self,
        state: GameState,
        remaining_depth: int | None = None,
    ) -> float:

        # Compute the natural logarithm of the uniformly weighted future-history count.

        path_count = self.future_history_count ( state, remaining_depth )

        # Return data to caller.

        return log ( path_count )

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

        # Evaluate the current state and every legal successor using the same configured horizon.

        # Create a fresh statistics accumulator for this decision.

        statistics               = _SearchStatistics ()
        current_state_path_count = self._count_future_histories ( state, self.horizon, statistics )
        current_state_entropy    = log ( current_state_path_count )
        action_scores = tuple (
            self._score_action (
                state                 = state,
                action                = action,
                current_state_entropy = current_state_entropy,
                statistics            = statistics,
            )
            for action in legal_actions
        )

        # Measure the best score needed for aligned output.

        best_score = max ( action_score.score for action_score in action_scores )
        best_actions = tuple (
            action_score.action
            for action_score in action_scores
            if isclose (
                action_score.score,
                best_score,
                rel_tol = SCORE_RELATIVE_TOLERANCE,
                abs_tol = SCORE_ABSOLUTE_TOLERANCE,
            )
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
                "horizon": self.horizon,
                "temperature": self.temperature,
                "tie_breaker": self.tie_breaker.value,
                "current_state_path_count": current_state_path_count,
                "current_state_entropy": current_state_entropy,
                "selected_action": selected_action,
                "evaluated_state_count": statistics.evaluated_state_count,
                "cache_hits": statistics.cache_hits,
            },
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _score_action
    #
    # Description:
    #
    #   Score action.
    #
    # Arguments:
    #
    #   state                 : Current immutable game state.
    #   action                : Tic-tac-toe board coordinate or candidate action.
    #   current_state_entropy : Entropy of the current state before applying the action.
    #   statistics            : Mutable diagnostic counters for one decision.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _score_action (
        self,
        state: GameState,
        action: Action,
        current_state_entropy: float,
        statistics: _SearchStatistics,
    ) -> ActionScore:

        # Count and score one successor without adding terminal utility or tactical adjustments.

        successor_state = self.game_rules.apply_action ( state, action )
        successor_path_count = self._count_future_histories (
            successor_state,
            self.horizon,
            statistics,
        )

        # Convert the successor path count into causal entropy.

        successor_entropy  = log ( successor_path_count )
        entropy_difference = successor_entropy - current_state_entropy
        scaled_score       = self.temperature * entropy_difference

        # Return data to caller.

        return ActionScore (
            action = action,
            score  = scaled_score,
            details = {
                "successor_path_count": successor_path_count,
                "successor_entropy": successor_entropy,
                "entropy_difference": entropy_difference,
                "temperature_scaled_score": scaled_score,
            },
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _count_future_histories
    #
    # Description:
    #
    #   Count future histories.
    #
    # Arguments:
    #
    #   state           : Current immutable game state.
    #   remaining_depth : Remaining recursive search depth.
    #   statistics      : Mutable diagnostic counters for one decision.
    #
    # Returns:
    #
    #   Integer value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _count_future_histories (
        self,
        state: GameState,
        remaining_depth: int,
        statistics: _SearchStatistics | None = None,
    ) -> int:

        # Reuse counts by immutable board and remaining depth.

        cache_key = ( state.board, remaining_depth )

        if cache_key in self._path_count_cache:
            if statistics is not None:
                statistics.cache_hits += 1

            # Return data to caller.

            return self._path_count_cache [ cache_key ]

        # Count this cache miss as a newly evaluated state.

        if statistics is not None:
            statistics.evaluated_state_count += 1

        # Apply the formal terminal and horizon-zero base case.

        if remaining_depth == 0 or state.is_terminal:
            path_count = 1
        else:
            path_count = sum (
                self._count_future_histories (
                    self.game_rules.apply_action ( state, action ),
                    remaining_depth - 1,
                    statistics,
                )
                for action in self.game_rules.legal_actions ( state )
            )

        # Cache the computed path count for this state and depth.

        self._path_count_cache [ cache_key ] = path_count

        # Return data to caller.

        return path_count
