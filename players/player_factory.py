#-----------------------------------------------------------------------------------------------------------------------
# Module:  player_factory.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Constructs independent runtime players from validated immutable player profiles.
#
#-----------------------------------------------------------------------------------------------------------------------

from random import Random

from domain.game_rules             import GameRules
from domain.mark                   import Mark
from domain.player                 import Player, PlayerProfile, PlayerType
from errors                        import ApplicationError
from intelligence.strategy_factory import StrategyFactory
from players.computer_player       import ComputerPlayer
from players.human_player          import HumanInput, HumanPlayer


#-----------------------------------------------------------------------------------------------------------------------
# Class: PlayerFactory
#
# Description:
#
#   Creates runtime players and delegates computer intelligence construction to the registered strategy factory.
#-----------------------------------------------------------------------------------------------------------------------

class PlayerFactory:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   game_rules       : Authoritative Tic-tac-toe rule service.
    #   strategy_factory : Factory used to construct configured strategies.
    #   random_generator : Shared random-number generator for stochastic choices.
    #   human_input      : Human input supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        game_rules: GameRules,
        strategy_factory: StrategyFactory,
        random_generator: Random,
        human_input: HumanInput | None = None,
    ) -> None:

        # Validate and retain shared composition dependencies.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "PlayerFactory requires a GameRules service." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( strategy_factory, StrategyFactory ):
            raise TypeError ( "PlayerFactory requires a StrategyFactory." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( random_generator, Random ):
            raise TypeError ( "PlayerFactory requires a random-number generator." )

        # Reject human input services that do not satisfy the protocol.

        if human_input is not None and not isinstance ( human_input, HumanInput ):
            raise TypeError ( "PlayerFactory human input must implement the HumanInput protocol." )

        # Store the validated player factory dependencies.

        self.game_rules       = game_rules
        self.strategy_factory = strategy_factory
        self.random_generator = random_generator
        self.human_input      = human_input

    #-------------------------------------------------------------------------------------------------------------------
    # Function: create
    #
    # Description:
    #
    #   Create one runtime player or strategy from validated configuration.
    #
    # Arguments:
    #
    #   profile : Validated player profile.
    #   mark    : Player mark assigned to the runtime player or board cell.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def create ( self, profile: PlayerProfile, mark: Mark ) -> Player:

        # Validate the requested runtime identity and mark assignment.

        if not isinstance ( profile, PlayerProfile ):
            raise TypeError ( "PlayerFactory requires a PlayerProfile." )

        # Reject mark values outside the supported set.

        if mark not in ( Mark.X, Mark.O ):
            raise ValueError ( "PlayerFactory requires an assigned X or O mark." )

        # Create a human player when the profile requests human control.

        if profile.player_type is PlayerType.HUMAN:

            # Handle the missing human input value before continuing.

            if self.human_input is None:

                raise ApplicationError ( "Human player construction requires a terminal input service." )

            # Return data to caller.

            return HumanPlayer (
                profile     = profile,
                mark        = mark,
                game_rules  = self.game_rules,
                human_input = self.human_input,
            )

        # Create the configured strategy for a computer player.

        strategy = self.strategy_factory.create (
            strategy_name = profile.intelligence_type,
            parameters    = profile.intelligence_parameters,
        )

        # Return data to caller.

        return ComputerPlayer (
            profile          = profile,
            mark             = mark,
            game_rules       = self.game_rules,
            strategy         = strategy,
            random_generator = self.random_generator,
        )
