#-----------------------------------------------------------------------------------------------------------------------
# Module:  random_strategy.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements uniform random action selection over the canonical legal-action set.
#
#-----------------------------------------------------------------------------------------------------------------------

from random import Random

from domain.action                      import Action
from domain.game_rules                  import GameRules
from domain.game_state                  import GameState
from domain.mark                        import Mark
from intelligence.intelligence_strategy import ActionScore, StrategyDecision, validate_strategy_request


#-----------------------------------------------------------------------------------------------------------------------
# Class: RandomStrategy
#
# Description:
#
#   Selects every legal action with equal probability through an injected random-number generator.
#-----------------------------------------------------------------------------------------------------------------------

class RandomStrategy:

    NAME = "random"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, game_rules: GameRules ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "RandomStrategy requires a GameRules service." )

        # Store the validated strategy dependencies.

        self.game_rules = game_rules

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

        # Assign equal probability to each legal random action.

        selection_probability = 1.0 / len ( legal_actions )
        action_scores = tuple (
            ActionScore (
                action  = action,
                score   = selection_probability,
                details = { "selection_probability": selection_probability },
            )
            for action in legal_actions
        )
        selected_action = random_generator.choice ( legal_actions )

        # Return data to caller.

        return StrategyDecision (
            action        = selected_action,
            strategy_name = self.name,
            action_scores = action_scores,
            metadata      = { "selection_method": "uniform_random" },
        )
