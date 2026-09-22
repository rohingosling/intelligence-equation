#-----------------------------------------------------------------------------------------------------------------------
# Module:  terminal_interface.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements stream-injected terminal input, game observation, result output, and replay coordination.
#
#-----------------------------------------------------------------------------------------------------------------------

from typing import TextIO

from configuration                      import PresentationConfiguration
from domain.game_state                  import GameState
from domain.history                     import MatchResult, MoveRecord
from domain.player                      import Player, PlayerType
from errors                             import InputEndedError
from intelligence.intelligence_strategy import StrategyDecision
from presentation.board_renderer        import BoardRenderer
from presentation.replay_renderer       import ReplayRenderer
from presentation.score_table_renderer  import ScoreTableRenderer


#-----------------------------------------------------------------------------------------------------------------------
# Class: TerminalInterface
#
# Description:
#
#   Provide the terminal boundary used by human players and match lifecycle observation.
#-----------------------------------------------------------------------------------------------------------------------

class TerminalInterface:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   input_stream               : Terminal stream used for player input.
    #   output_stream              : Terminal stream used for match output.
    #   presentation_configuration : Presentation configuration supplied to the operation.
    #   board_renderer             : Board renderer supplied to the operation.
    #   replay_renderer            : Replay renderer supplied to the operation.
    #   score_table_renderer       : Score table renderer supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        input_stream: TextIO,
        output_stream: TextIO,
        presentation_configuration: PresentationConfiguration,
        board_renderer: BoardRenderer | None            = None,
        replay_renderer: ReplayRenderer | None          = None,
        score_table_renderer: ScoreTableRenderer | None = None,
    ) -> None:

        # Validate and retain stream and presentation dependencies.

        # Require the input stream to provide readline().

        if not hasattr ( input_stream, "readline" ):
            raise TypeError ( "TerminalInterface requires a readable input stream." )

        # Require the output stream to provide write().

        if not hasattr ( output_stream, "write" ):
            raise TypeError ( "TerminalInterface requires a writable output stream." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( presentation_configuration, PresentationConfiguration ):
            raise TypeError ( "TerminalInterface requires presentation configuration." )

        # Resolve the optional board renderer dependency.

        resolved_board_renderer = board_renderer or BoardRenderer (
            use_unicode = self._supports_unicode ( output_stream ),
        )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( resolved_board_renderer, BoardRenderer ):
            raise TypeError ( "TerminalInterface requires a BoardRenderer." )

        # Resolve the optional score table renderer dependency.

        resolved_score_table_renderer = score_table_renderer or ScoreTableRenderer (
            use_unicode = resolved_board_renderer.use_unicode,
        )
        if not isinstance ( resolved_score_table_renderer, ScoreTableRenderer ):
            raise TypeError ( "TerminalInterface requires a ScoreTableRenderer." )

        # Resolve the optional replay renderer dependency.

        resolved_replay_renderer = replay_renderer or ReplayRenderer (
            board_renderer       = resolved_board_renderer,
            score_table_renderer = resolved_score_table_renderer,
        )
        if not isinstance ( resolved_replay_renderer, ReplayRenderer ):
            raise TypeError ( "TerminalInterface requires a ReplayRenderer." )

        # Store the validated terminal presentation dependencies.

        self.input_stream               = input_stream
        self.output_stream              = output_stream
        self.presentation_configuration = presentation_configuration
        self.board_renderer             = resolved_board_renderer
        self.replay_renderer            = resolved_replay_renderer
        self.score_table_renderer       = resolved_score_table_renderer

    #-------------------------------------------------------------------------------------------------------------------
    # Function: request_coordinate
    #
    # Description:
    #
    #   Prompt one human player and return the entered coordinate text.
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

        # Display the human-turn prompt on the same line as the terminal input.

        self._write ( f"[Human: {player_name}] " )
        coordinate_text = self.input_stream.readline ()

        # Treat end-of-input as a stopped interactive session.

        if coordinate_text == "":
            raise InputEndedError ( f"Input ended during {player_name}'s turn." )

        # Return data to caller.

        return coordinate_text

    #-------------------------------------------------------------------------------------------------------------------
    # Function: show_input_error
    #
    # Description:
    #
    #   Display one recoverable human-input diagnostic.
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

        self._write_line ()
        self._write_line ( f"Invalid move: {message}" )
        self._write_line ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_game_started
    #
    # Description:
    #
    #   Display the configured players and the empty Move 0 board.
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

        player_labels = (
            f"Player 1 ({self._profile_type_label ( players [ 0 ].profile.player_type )})",
            f"Player 2 ({self._profile_type_label ( players [ 1 ].profile.player_type )})",
        )
        label_width = max ( len ( label ) for label in player_labels )

        # Write the next terminal output line.

        self._write_line ()
        self._write_line ( f"{player_labels [ 0 ].ljust ( label_width )} : {players [ 0 ].profile.name}" )
        self._write_line ( f"{player_labels [ 1 ].ljust ( label_width )} : {players [ 1 ].profile.name}" )
        self._write_board (
            state                = state,
            caption              = "Move 0",
            trailing_blank_lines = 2,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_move_completed
    #
    # Description:
    #
    #   Display one accepted move and its immutable successor board.
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

        if (
            record.player_type is PlayerType.COMPUTER
            and self.presentation_configuration.show_computer_scores
        ):
            self._write_computer_scores ( record )

        # Echo computer moves so automated runs show the selected action.

        if record.player_type is PlayerType.COMPUTER:
            self._write_line ( f"[Computer: {record.player_name}] {record.action}" )

        # Choose the spacing that follows the rendered move board.

        trailing_blank_lines = 1 if record.state_after.is_terminal else 2

        # Render the board produced by this move.

        self._write_board (
            state                = record.state_after,
            caption              = f"Move {record.move_number}",
            trailing_blank_lines = trailing_blank_lines,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: on_game_completed
    #
    # Description:
    #
    #   Display the final result and optional immutable-history replay.
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

        # Handle the missing result.winner value before continuing.

        if result.winner is None:
            self._write_line ( "Draw" )
        else:
            controller_label = (
                "Human"
                if result.winner.profile.player_type is PlayerType.HUMAN
                else "Computer"
            )
            self._write_line ( f"[{controller_label}: {result.winner.profile.name}] Wins" )

        # Render the replay section when presentation settings request it.

        if self.presentation_configuration.show_replay:

            self._write_line ()
            self._write_line ( "Replay..." )
            self._write_line ()

            # Write each rendered replay line.

            for replay_line in self.replay_renderer.render (
                history              = result.history,
                boards_per_row       = self.presentation_configuration.replay_boards_per_row,
                show_computer_scores = self.presentation_configuration.show_computer_scores,
            ):
                self._write_line ( replay_line )

            # Write the next terminal output line.

            self._write_line ()
            self._write_line ()
        else:
            self._write_line ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _write_board
    #
    # Description:
    #
    #   Write one captioned board and a separating blank line.
    #
    # Arguments:
    #
    #   state                : Current immutable game state.
    #   caption              : Caption supplied to the operation.
    #   trailing_blank_lines : Trailing blank lines supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _write_board ( self, state: GameState, caption: str, trailing_blank_lines: int ) -> None:

        # Write board.

        self._write_line ()
        self._write_line ( f"   {caption}" )

        # Write each rendered board line.

        for board_line in self.board_renderer.render ( state ):
            self._write_line ( board_line.rstrip () )

        # Write the requested number of trailing blank lines.

        for _ in range ( trailing_blank_lines ):
            self._write_line ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _write_computer_scores
    #
    # Description:
    #
    #   Write one concise table of structured computer candidate scores.
    #
    # Arguments:
    #
    #   record : Accepted move record to render or publish.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _write_computer_scores ( self, record: MoveRecord ) -> None:

        # Write computer scores.

        diagnostics = record.decision.diagnostics

        # Skip computer score output when diagnostics are absent or empty.

        if not isinstance ( diagnostics, StrategyDecision ) or not diagnostics.action_scores:
            return

        # Write each rendered score table line.

        for score_line in self.score_table_renderer.render ( diagnostics ):
            self._write_line ( score_line )

        # Write the next terminal output line.

        self._write_line ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _write_line
    #
    # Description:
    #
    #   Write and flush one terminal line.
    #
    # Arguments:
    #
    #   text : Text supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _write_line ( self, text: str = "" ) -> None:

        # Write line.

        self._write ( f"{text}\n" )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _write
    #
    # Description:
    #
    #   Write and flush terminal text without adding a newline.
    #
    # Arguments:
    #
    #   text : Text supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _write ( self, text: str ) -> None:

        # Write and flush the text so terminal output appears immediately.

        self.output_stream.write ( text )
        self.output_stream.flush ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _profile_type_label
    #
    # Description:
    #
    #   Convert a profile control type to the match-header label.
    #
    # Arguments:
    #
    #   player_type : Player type supplied to the operation.
    #
    # Returns:
    #
    #   Text value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _profile_type_label ( player_type: PlayerType ) -> str:

        # Return data to caller.

        return "Human" if player_type is PlayerType.HUMAN else "AI"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _supports_unicode
    #
    # Description:
    #
    #   Report whether a stream encoding can represent the Unicode board characters.
    #
    # Arguments:
    #
    #   output_stream : Terminal stream used for match output.
    #
    # Returns:
    #
    #   Boolean result.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _supports_unicode ( output_stream: TextIO ) -> bool:

        # Supports unicode.

        encoding = getattr ( output_stream, "encoding", None )

        if encoding is None:

            # In-memory text streams accept Unicode directly.

            return True

        try:
            "┌─┬┐│├┼┤└┴┘".encode ( encoding )
        except ( LookupError, UnicodeEncodeError ):

            # Return data to caller.

            return False

        # Return data to caller.

        return True
