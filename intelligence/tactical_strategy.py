#-----------------------------------------------------------------------------------------------------------------------
# Module:  tactical_strategy.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements immediate wins, immediate-loss prevention, and positional Tic-tac-toe priorities.
#
#-----------------------------------------------------------------------------------------------------------------------

from random import Random

from domain.action                      import Action
from domain.game_rules                  import GameRules
from domain.game_state                  import GameState
from domain.mark                        import Mark
from intelligence.intelligence_strategy import ActionScore, StrategyDecision, validate_strategy_request
from intelligence.tie_breaking          import TieBreaker, parse_tie_breaker, select_tied_action


CENTER_ACTION = Action.parse ( "b2" )
CORNER_ACTIONS = frozenset (
    (
        Action.parse ( "a1" ),
        Action.parse ( "c1" ),
        Action.parse ( "a3" ),
        Action.parse ( "c3" ),
    )
)

PRIORITY_IMMEDIATE_WIN = 5
PRIORITY_BLOCK         = 4
PRIORITY_CENTER        = 3
PRIORITY_CORNER        = 2
PRIORITY_EDGE          = 1


#-----------------------------------------------------------------------------------------------------------------------
# Class: TacticalStrategy
#
# Description:
#
#   Applies the required win, block, center, corner, and edge priorities with configurable tie-breaking.
#-----------------------------------------------------------------------------------------------------------------------

class TacticalStrategy:

    NAME = "tactical"

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
            raise TypeError ( "TacticalStrategy requires a GameRules service." )

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

        # Find tactical moves that win immediately.

        immediate_winning_actions = self._find_immediate_winning_actions (
            state         = state,
            acting_mark   = acting_mark,
            legal_actions = legal_actions,
        )

        # Find tactical moves that block the opponent from winning next.

        threatened_actions = self._find_threatened_actions (
            state         = state,
            acting_mark   = acting_mark,
            legal_actions = legal_actions,
        )

        # Build the immutable action scores collection.

        action_scores = tuple (
            self._score_action ( action, immediate_winning_actions, threatened_actions )
            for action in legal_actions
        )

        # Measure the best score needed for aligned output.

        best_score = max ( action_score.score for action_score in action_scores )
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
            metadata      = { "tie_breaker": self.tie_breaker.value },
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _find_immediate_winning_actions
    #
    # Description:
    #
    #   Find immediate winning actions.
    #
    # Arguments:
    #
    #   state         : Current immutable game state.
    #   acting_mark   : Mark assigned to the strategy for the current decision.
    #   legal_actions : Canonical legal actions available in the current state.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _find_immediate_winning_actions (
        self,
        state: GameState,
        acting_mark: Mark,
        legal_actions: tuple [ Action, ... ],
    ) -> frozenset [ Action ]:

        # Find legal actions that immediately complete a win for the acting player.

        winning_actions = frozenset (
            action
            for action in legal_actions
            if self.game_rules.apply_action ( state, action ).outcome.winner is acting_mark
        )

        # Return data to caller.

        return winning_actions

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _find_threatened_actions
    #
    # Description:
    #
    #   Find threatened actions.
    #
    # Arguments:
    #
    #   state         : Current immutable game state.
    #   acting_mark   : Mark assigned to the strategy for the current decision.
    #   legal_actions : Canonical legal actions available in the current state.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _find_threatened_actions (
        self,
        state: GameState,
        acting_mark: Mark,
        legal_actions: tuple [ Action, ... ],
    ) -> frozenset [ Action ]:

        # Find cells where the opponent can win immediately unless the acting player occupies that cell.

        opponent_mark = acting_mark.opponent ()
        threatened_actions: set [ Action ] = set ()

        # Test each provisional move for immediate tactical consequences.

        for provisional_action in legal_actions:
            provisional_state = self.game_rules.apply_action ( state, provisional_action )

            # Treat a terminal provisional state as a direct tactical result.

            if provisional_state.is_terminal:
                continue

            # Check every opponent reply for a winning threat.

            for opponent_action in self.game_rules.legal_actions ( provisional_state ):
                opponent_successor = self.game_rules.apply_action ( provisional_state, opponent_action )

                # Record provisional moves that allow the opponent to win next.

                if opponent_successor.outcome.winner is opponent_mark:
                    threatened_actions.add ( opponent_action )

        # Return data to caller.

        return frozenset ( threatened_actions )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _score_action
    #
    # Description:
    #
    #   Score action.
    #
    # Arguments:
    #
    #   action                    : Tic-tac-toe board coordinate or candidate action.
    #   immediate_winning_actions : Immediate winning actions supplied to the operation.
    #   threatened_actions        : Threatened actions supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _score_action (
        action: Action,
        immediate_winning_actions: frozenset [ Action ],
        threatened_actions: frozenset [ Action ],
    ) -> ActionScore:

        # Assign the highest applicable tactical priority.

        if action in immediate_winning_actions:
            score    = PRIORITY_IMMEDIATE_WIN
            category = "immediate_win"

        elif action in threatened_actions:
            score    = PRIORITY_BLOCK
            category = "block"

        elif action == CENTER_ACTION:
            score    = PRIORITY_CENTER
            category = "center"

        elif action in CORNER_ACTIONS:
            score    = PRIORITY_CORNER
            category = "corner"

        else:
            score    = PRIORITY_EDGE
            category = "edge"

        # Return data to caller.

        return ActionScore (
            action  = action,
            score   = score,
            details = { "category": category },
        )
