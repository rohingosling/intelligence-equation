#-----------------------------------------------------------------------------------------------------------------------
# Module:  replay_renderer.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Formats immutable accepted-move history as rows of side-by-side board snapshots.
#
#-----------------------------------------------------------------------------------------------------------------------

from domain.history                     import GameHistory, MoveRecord
from domain.outcome                     import OutcomeStatus
from domain.player                      import PlayerType
from intelligence.intelligence_strategy import StrategyDecision
from presentation.board_renderer        import BoardRenderer
from presentation.score_table_renderer  import ScoreTableRenderer


BOARD_SPACING = "    "


#-----------------------------------------------------------------------------------------------------------------------
# Class: ReplayRenderer
#
# Description:
#
#   Compose complete move-history snapshots into aligned multi-board replay rows.
#-----------------------------------------------------------------------------------------------------------------------

class ReplayRenderer:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   board_renderer       : Board renderer supplied to the operation.
    #   score_table_renderer : Score table renderer supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ (
        self,
        board_renderer: BoardRenderer,
        score_table_renderer: ScoreTableRenderer | None = None,
    ) -> None:

        # Validate and retain the pure board and score formatters.

        if not isinstance ( board_renderer, BoardRenderer ):
            raise TypeError ( "ReplayRenderer requires a BoardRenderer." )

        # Resolve the optional score table renderer dependency.

        resolved_score_table_renderer = score_table_renderer or ScoreTableRenderer (
            use_unicode = board_renderer.use_unicode,
        )

        # Reject score table renderers that do not satisfy the required type.

        if not isinstance ( resolved_score_table_renderer, ScoreTableRenderer ):
            raise TypeError ( "ReplayRenderer requires a ScoreTableRenderer." )

        # Store the resolved replay rendering dependencies.

        self.board_renderer       = board_renderer
        self.score_table_renderer = resolved_score_table_renderer

    #-------------------------------------------------------------------------------------------------------------------
    # Function: render
    #
    # Description:
    #
    #   Render every post-move history snapshot in configured row groups.
    #
    # Arguments:
    #
    #   history              : Immutable accepted-move history.
    #   boards_per_row       : Maximum number of boards in one replay row.
    #   show_computer_scores : Whether computer diagnostics are included below each computer move.
    #
    # Returns:
    #
    #   Replay lines containing every post-move board and caption.
    #-------------------------------------------------------------------------------------------------------------------

    def render (
        self,
        history: GameHistory,
        boards_per_row: int,
        show_computer_scores: bool = False,
    ) -> list [ str ]:

        #-----------------------------
        # Validate the replay request.
        #-----------------------------

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( history, GameHistory ):
            raise TypeError ( "ReplayRenderer requires an immutable GameHistory." )

        # Reject invalid replay column counts.

        if type ( boards_per_row ) is not int or boards_per_row < 1:
            raise ValueError ( "Replay boards per row must be a positive integer." )

        # Reject non-boolean computer-score visibility flags.

        if type ( show_computer_scores ) is not bool:
            raise TypeError ( "Computer-score replay visibility must be a boolean." )

        # Initialize the replay lines accumulator.

        replay_lines = []

        #-----------------------------------------------------------------------
        # Compose each complete or partial row through equal-width line joining.
        #-----------------------------------------------------------------------

        # Render the replay in rows of board blocks.

        for row_start in range ( 0, len ( history ), boards_per_row ):

            # Select the move records for the current replay row.

            row_records = history.records [ row_start : row_start + boards_per_row ]
            row_blocks = tuple (
                self._render_record (
                    record               = record,
                    is_final             = record.move_number == len ( history ),
                    show_computer_scores = show_computer_scores,
                )
                for record in row_records
            )

            # Build the immutable block widths collection.

            block_widths = tuple ( max ( len ( line ) for line in block ) for block in row_blocks )
            block_height = max ( len ( block ) for block in row_blocks )

            # Stitch together corresponding lines from each board block.

            for line_index in range ( block_height ):

                # Join the current row of board-block lines with horizontal spacing.

                joined_line = BOARD_SPACING.join (
                    (
                        block [ line_index ]
                        if line_index < len ( block )
                        else ""
                    ).ljust ( block_width )
                    for block, block_width in zip ( row_blocks, block_widths )
                )

                # Append the stitched replay line without trailing padding.

                replay_lines.append ( joined_line.rstrip () )

            # Separate replay rows with blank lines.

            if row_start + boards_per_row < len ( history ):
                replay_lines.append ( "" )
                replay_lines.append ( "" )

        # Return data to caller.

        return replay_lines

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _render_record
    #
    # Description:
    #
    #   Render one history snapshot and its move caption.
    #
    # Arguments:
    #
    #   record               : Accepted move record to render or publish.
    #   is_final             : Is final supplied to the operation.
    #   show_computer_scores : Show computer scores supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _render_record (
        self,
        record: MoveRecord,
        is_final: bool,
        show_computer_scores: bool,
    ) -> list [ str ]:

        # Render record.

        board_lines = self.board_renderer.render ( record.state_after )
        caption     = f"Move {record.move_number}"

        # Annotate the final replay board with the game result.

        if is_final:

            # Distinguish wins from draws in the final replay caption.

            if record.state_after.outcome.status is OutcomeStatus.WIN:
                caption += f" ({record.state_after.outcome.winner.value} Wins)"
            else:
                caption += " (Draw)"

        # Render score diagnostics for the current replay record.

        score_lines = self._render_score_lines (
            record               = record,
            show_computer_scores = show_computer_scores,
        )

        # Add score diagnostics above the rendered board when present.

        if score_lines:

            # Return data to caller.

            return [ f"   {caption}" ] + board_lines + [ "" ] + score_lines

        # Return data to caller.

        return [ f"   {caption}" ] + board_lines

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _render_score_lines
    #
    # Description:
    #
    #   Render optional computer diagnostics for one replay block.
    #
    # Arguments:
    #
    #   record               : Accepted move record to render or publish.
    #   show_computer_scores : Show computer scores supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _render_score_lines ( self, record: MoveRecord, show_computer_scores: bool ) -> list [ str ]:

        # Render score lines.

        if not show_computer_scores or record.player_type is not PlayerType.COMPUTER:

            # Return data to caller.

            return []

        # Read strategy diagnostics attached to the move decision.

        diagnostics = record.decision.diagnostics

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( diagnostics, StrategyDecision ):

            # Return data to caller.

            return []

        # Return data to caller.

        return self.score_table_renderer.render ( diagnostics )
