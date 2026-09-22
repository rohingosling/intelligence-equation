#-----------------------------------------------------------------------------------------------------------------------
# Module:  score_table_renderer.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Formats structured computer-strategy diagnostics as stable terminal score tables.
#
#-----------------------------------------------------------------------------------------------------------------------

from intelligence.intelligence_strategy import StrategyDecision

TABLE_COLUMN_SPACING    = "  "
UNICODE_SELECTED_MARKER = "◄──"
ASCII_SELECTED_MARKER   = "<--"

#-----------------------------------------------------------------------------------------------------------------------
# Class: ScoreTableRenderer
#
# Description:
#
#   Render one strategy decision's candidate scores as plain terminal lines.
#-----------------------------------------------------------------------------------------------------------------------

class ScoreTableRenderer:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   use_unicode : Use unicode supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, use_unicode: bool = True ) -> None:

        # Retain the selected terminal-character mode.

        if type ( use_unicode ) is not bool:
            raise TypeError ( "ScoreTableRenderer Unicode mode must be a boolean." )

        self.use_unicode = use_unicode

    #-------------------------------------------------------------------------------------------------------------------
    # Function: render
    #
    # Description:
    #
    #   Render one computer strategy decision and candidate-score table.
    #
    # Arguments:
    #
    #   decision : Structured strategy diagnostics for one accepted computer move.
    #
    # Returns:
    #
    #   Score-table lines, or no lines when no candidate scores were recorded.
    #-------------------------------------------------------------------------------------------------------------------

    def render ( self, decision: StrategyDecision ) -> list [ str ]:

        # Validate the score-table request.

        if not isinstance ( decision, StrategyDecision ):
            raise TypeError ( "ScoreTableRenderer requires a StrategyDecision." )

        # Skip score rendering when no action scores are available.

        if not decision.action_scores:

            # Return data to caller.

            return []

        # Render the score table with deterministic terminal text.

        # Return data to caller.

        return [
            f"Computer scores ({decision.strategy_name}):",
            "",
        ] + self._render_score_table ( decision )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _render_score_table
    #
    # Description:
    #
    #   Render a simple aligned score table for Unicode and ASCII terminals.
    #
    # Arguments:
    #
    #   decision : Strategy or player decision returned by the caller.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _render_score_table ( self, decision: StrategyDecision ) -> list [ str ]:

        # Render the aligned score rows.

        rows = tuple (
            (
                str ( action_score.action ),
                self._format_score ( action_score.score ),
                self._selected_marker () if action_score.action == decision.action else "",
            )
            for action_score in decision.action_scores
        )

        # Measure the widths needed for aligned output.

        action_width   = max ( len ( "Action" ), *( len ( row [ 0 ] ) for row in rows ) )
        score_width    = max ( len ( "Score" ), *( len ( row [ 1 ] ) for row in rows ) ) + 1
        selected_width = len ( "Selected" )
        header_line = self._format_plain_score_row (
            action_text    = "Action",
            score_text     = "Score",
            selected_text  = "Selected",
            action_width   = action_width,
            score_width    = score_width,
            selected_width = selected_width,
        )
        separator_line = self._separator_character () * len ( header_line )

        # Return data to caller.

        return [ header_line, separator_line ] + [
            self._format_plain_score_row (
                action_text    = row [ 0 ],
                score_text     = row [ 1 ],
                selected_text  = row [ 2 ],
                action_width   = action_width,
                score_width    = score_width,
                selected_width = selected_width,
            )
            for row in rows
        ]

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _format_plain_score_row
    #
    # Description:
    #
    #   Format one ASCII score-table row with aligned score and selected columns.
    #
    # Arguments:
    #
    #   action_text    : Action text supplied to the operation.
    #   score_text     : Score text supplied to the operation.
    #   selected_text  : Selected text supplied to the operation.
    #   action_width   : Action width supplied to the operation.
    #   score_width    : Score width supplied to the operation.
    #   selected_width : Selected width supplied to the operation.
    #
    # Returns:
    #
    #   Text value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _format_plain_score_row (
        action_text: str,
        score_text: str,
        selected_text: str,
        action_width: int,
        score_width: int,
        selected_width: int,
    ) -> str:

        # Return data to caller.

        return (
            f"{action_text:<{action_width}}"
            f"{TABLE_COLUMN_SPACING}"
            f"{score_text:>{score_width}}"
            f"{TABLE_COLUMN_SPACING}"
            f"{selected_text:<{selected_width}}"
        ).rstrip ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _separator_character
    #
    # Description:
    #
    #   Return the score-table separator character for the configured terminal mode.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Separator character.
    #-------------------------------------------------------------------------------------------------------------------

    def _separator_character ( self ) -> str:

        # Return data to caller.

        return "─" if self.use_unicode else "-"

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _selected_marker
    #
    # Description:
    #
    #   Return the selected-action marker for the configured terminal mode.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Marker text.
    #-------------------------------------------------------------------------------------------------------------------

    def _selected_marker ( self ) -> str:

        # Return data to caller.

        return UNICODE_SELECTED_MARKER if self.use_unicode else ASCII_SELECTED_MARKER

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _format_score
    #
    # Description:
    #
    #   Format one finite strategy score compactly while preserving integer values.
    #
    # Arguments:
    #
    #   score : Score supplied to the operation.
    #
    # Returns:
    #
    #   Text value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _format_score ( score: int | float ) -> str:

        # Format score.

        if isinstance ( score, int ):

            # Return data to caller.

            return str ( score )

        # Return data to caller.

        return f"{score:.6f}"
