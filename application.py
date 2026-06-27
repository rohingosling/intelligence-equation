#-----------------------------------------------------------------------------------------------------------------------
# Module:  application.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines command-line parsing, validated composition, terminal presentation, match execution, and error handling.
#
#-----------------------------------------------------------------------------------------------------------------------

from argparse        import ArgumentParser
from collections.abc import Sequence
from sys             import stderr, stdin, stdout
from contextlib      import redirect_stderr, redirect_stdout
from pathlib         import Path
from random          import Random
from typing          import TextIO

from configuration                 import ConfigurationLoader
from domain.game                   import Game
from domain.game_rules             import GameRules
from domain.history                import MatchResult
from domain.mark                   import Mark
from errors                        import ApplicationError
from intelligence.strategy_factory import StrategyFactory
from players.player_factory        import PlayerFactory
from presentation                  import TerminalInterface

#-----------------------------------------------------------------------------------------------------------------------
# Class: Application
#
# Description:
#
#   Coordinate the application lifecycle from command-line configuration through one complete match.
#-----------------------------------------------------------------------------------------------------------------------

class Application:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   input_stream  : Terminal stream used for player input.
    #   output_stream : Terminal stream used for match output.
    #   error_stream  : Terminal stream used for diagnostic output.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        input_stream: TextIO | None  = None,
        output_stream: TextIO | None = None,
        error_stream: TextIO | None  = None,
    ) -> None:

        # Resolve injectable terminal streams.

        self.input_stream  = input_stream if input_stream is not None else stdin
        self.output_stream = output_stream if output_stream is not None else stdout
        self.error_stream  = error_stream if error_stream is not None else stderr

    #-------------------------------------------------------------------------------------------------------------------
    # Function: run
    #
    # Description:
    #
    #   Parse the command line and execute the configured match.
    #
    # Arguments:
    #
    #   arguments : Optional command-line arguments used by tests and embedded callers.
    #
    # Returns:
    #
    #   Process exit status.
    #-------------------------------------------------------------------------------------------------------------------

    def run ( self, arguments: Sequence [ str ] | None = None ) -> int:

        # Parse the command line and execute the configured match with concise diagnostics.

        argument_parser = self._create_argument_parser ()

        # Parse arguments while routing parser output through the configured streams.

        try:
            with redirect_stdout ( self.output_stream ), redirect_stderr ( self.error_stream ):
                parsed_arguments = argument_parser.parse_args ( arguments )

        except SystemExit as error:

            # Return data to caller.

            return int ( error.code )

        # Run the selected configuration and translate application errors into exit codes.

        try:
            self.play_configuration ( parsed_arguments.configuration_path )
        except ApplicationError as error:
            print ( f"Error: {error}", file = self.error_stream )

            # Return data to caller.

            return 1

        except Exception as error:
            print ( f"Error: Unexpected internal failure: {error}", file = self.error_stream )

            # Return data to caller.

            return 1

        # Return data to caller.

        return 0

    #-------------------------------------------------------------------------------------------------------------------
    # Function: play_configuration
    #
    # Description:
    #
    #   Load one validated YAML configuration and execute its terminal-presented match.
    #
    # Arguments:
    #
    #   configuration_path : Path to the YAML player and match configuration.
    #
    # Returns:
    #
    #   The completed immutable match result.
    #-------------------------------------------------------------------------------------------------------------------

    def play_configuration ( self, configuration_path: str | Path ) -> MatchResult:

        # Construct the validation dependencies and load configuration before runtime game composition.

        game_rules       = GameRules ()
        strategy_factory = StrategyFactory ( game_rules )
        configuration    = ConfigurationLoader ( strategy_factory ).load ( configuration_path )

        # Construct terminal presentation and independent runtime players.

        random_generator = Random ( configuration.application.random_seed )
        terminal_interface = TerminalInterface (
            input_stream               = self.input_stream,
            output_stream              = self.output_stream,
            presentation_configuration = configuration.presentation,
        )

        # Create the player factory after all strategy and presentation dependencies are ready.

        player_factory = PlayerFactory (
            game_rules       = game_rules,
            strategy_factory = strategy_factory,
            random_generator = random_generator,
            human_input      = terminal_interface,
        )
        player_x = player_factory.create ( configuration.player_1_profile, Mark.X )
        player_o = player_factory.create ( configuration.player_2_profile, Mark.O )

        # Execute and return the configured match.

        return Game ( game_rules, terminal_interface ).play ( player_x, player_o )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _create_argument_parser
    #
    # Description:
    #
    #   Create the parser for the public command-line contract.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   The configured argument parser.
    #-------------------------------------------------------------------------------------------------------------------

    def _create_argument_parser ( self ) -> ArgumentParser:

        # Create the parser for the public command-line contract.

        argument_parser = ArgumentParser (
            prog        = "python main.py",
            description = "Intelligence Equation Tic-Tac-Toe",
        )

        # Register the configuration path command-line argument.

        argument_parser.add_argument (
            "configuration_path",
            metavar = "configuration.yaml",
            help    = "Path to the YAML player and match configuration.",
        )

        # Return data to caller.

        return argument_parser
