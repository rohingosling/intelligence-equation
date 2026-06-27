#-----------------------------------------------------------------------------------------------------------------------
# Module:  computer_player.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements a runtime computer player that delegates action selection to one intelligence strategy.
#
#-----------------------------------------------------------------------------------------------------------------------

from random import Random

from domain.game_rules                  import GameRules
from domain.game_state                  import GameState
from domain.mark                        import Mark
from domain.player                      import PlayerDecision, PlayerProfile, PlayerType
from errors                             import StrategyContractError
from intelligence.intelligence_strategy import IntelligenceStrategy, validate_strategy_decision


#-----------------------------------------------------------------------------------------------------------------------
# Class: ComputerPlayer
#
# Description:
#
#   Binds a computer profile and assigned mark to one strategy and one injected random-number generator.
#-----------------------------------------------------------------------------------------------------------------------

class ComputerPlayer:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   profile          : Validated player profile.
    #   mark             : Player mark assigned to the runtime player or board cell.
    #   game_rules       : Authoritative Tic-tac-toe rule service.
    #   strategy         : Computer strategy instance.
    #   random_generator : Shared random-number generator for stochastic choices.
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
        strategy: IntelligenceStrategy,
        random_generator: Random,
    ) -> None:

        # Validate the runtime player identity and dependencies.

        # Reject computer players built from non-computer profiles.

        if not isinstance ( profile, PlayerProfile ) or profile.player_type is not PlayerType.COMPUTER:
            raise TypeError ( "ComputerPlayer requires a computer PlayerProfile." )

        # Reject mark values outside the supported set.

        if mark not in ( Mark.X, Mark.O ):
            raise ValueError ( "ComputerPlayer requires an assigned X or O mark." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "ComputerPlayer requires a GameRules service." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( strategy, IntelligenceStrategy ):
            raise TypeError ( "ComputerPlayer requires an IntelligenceStrategy." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( random_generator, Random ):
            raise TypeError ( "ComputerPlayer requires an injected random-number generator." )

        # Detect when profile.intelligence type differs from the expected value.

        if profile.intelligence_type != strategy.name:
            raise ValueError ( "Computer profile intelligence type must match the assigned strategy." )

        # Store the validated computer player dependencies.

        self.profile          = profile
        self.mark             = mark
        self.game_rules       = game_rules
        self.strategy         = strategy
        self.random_generator = random_generator

    #-------------------------------------------------------------------------------------------------------------------
    # Function: choose_action
    #
    # Description:
    #
    #   Choose one legal action for the current game state.
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

        # Validate that this runtime player owns the current turn.

        if not isinstance ( state, GameState ):
            raise StrategyContractError ( "Computer players require an immutable GameState." )

        # Validate the supplied game state before selecting an action.

        self.game_rules.validate_state ( state )

        if state.is_terminal:
            raise StrategyContractError ( "Computer players cannot choose an action from a terminal state." )

        # Reject decisions requested for the wrong player's turn.

        if self.game_rules.player_to_move ( state ) is not self.mark:
            raise StrategyContractError ( "Computer player mark does not match the state player to move." )

        # Collect legal actions for the current turn.

        legal_actions = self.game_rules.legal_actions ( state )
        strategy_decision = self.strategy.select_action (
            state            = state,
            acting_mark      = self.mark,
            legal_actions    = legal_actions,
            random_generator = self.random_generator,
        )

        # Validate the strategy decision before returning it as the player decision.

        validate_strategy_decision (
            decision      = strategy_decision,
            strategy_name = self.strategy.name,
            legal_actions = legal_actions,
        )

        # Return data to caller.

        return PlayerDecision (
            action      = strategy_decision.action,
            diagnostics = strategy_decision,
        )
