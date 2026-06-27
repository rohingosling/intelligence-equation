#-----------------------------------------------------------------------------------------------------------------------
# Module:  board_renderer.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Formats immutable Tic-tac-toe states as stable-width Unicode terminal boards.
#
#-----------------------------------------------------------------------------------------------------------------------

from domain.action     import Action
from domain.game_state import GameState
from domain.mark       import Mark
from domain.outcome    import OutcomeStatus


BOARD_SIZE = 3


#-----------------------------------------------------------------------------------------------------------------------
# Class: BoardRenderer
#
# Description:
#
#   Render one immutable game-state snapshot without performing terminal output.
#-----------------------------------------------------------------------------------------------------------------------

class BoardRenderer:

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
            raise TypeError ( "BoardRenderer Unicode mode must be a boolean." )

        self.use_unicode = use_unicode

    #-------------------------------------------------------------------------------------------------------------------
    # Function: render
    #
    # Description:
    #
    #   Render one board with optional row and column labels.
    #
    # Arguments:
    #
    #   state               : Immutable game-state snapshot to render.
    #   include_coordinates : Whether to include row and column labels.
    #
    # Returns:
    #
    #   Stable-width Unicode board lines.
    #-------------------------------------------------------------------------------------------------------------------

    def render ( self, state: GameState, include_coordinates: bool = True ) -> list [ str ]:

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( state, GameState ):
            raise TypeError ( "BoardRenderer requires an immutable GameState." )

        # Reject non-boolean coordinate visibility flags.

        if type ( include_coordinates ) is not bool:
            raise TypeError ( "Board coordinate visibility must be a boolean." )

        # Resolve which cells should be highlighted in the rendered board.

        highlighted_actions = self._highlighted_actions ( state )
        row_prefixes        = ( " 1 ", " 2 ", " 3 " ) if include_coordinates else ( "", "", "" )
        border_prefix       = "   " if include_coordinates else ""
        board_lines         = []

        # Resolve the border characters for the selected rendering mode.

        top_border, middle_border, bottom_border, vertical_border = self._border_characters ()

        # Append the top board border.

        board_lines.append ( f"{border_prefix}{top_border}" )

        # Render each board row.

        for row in range ( BOARD_SIZE ):

            cell_contents = []

            # Render each cell in the current row.

            for column in range ( BOARD_SIZE ):
                action = Action ( row = row, column = column )
                mark   = state.board.mark_at ( action )
                cell_contents.append ( self._render_cell ( mark, action in highlighted_actions ) )

            # Append the rendered row to the board output.

            board_lines.append (
                f"{row_prefixes [ row ]}{vertical_border}"
                f"{vertical_border.join ( cell_contents )}{vertical_border}"
            )

            # Insert a middle border between board rows.

            if row < BOARD_SIZE - 1:
                board_lines.append ( f"{border_prefix}{middle_border}" )

        board_lines.append ( f"{border_prefix}{bottom_border}" )

        if include_coordinates:
            board_lines.append ( "     A   B   C" )

        # Pad every line to the same width for replay composition.

        board_width = max ( len ( line ) for line in board_lines )

        # Return data to caller.

        return [ line.ljust ( board_width ) for line in board_lines ]

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _highlighted_actions
    #
    # Description:
    #
    #   Return every cell belonging to any completed winning line.
    #
    # Arguments:
    #
    #   state : Current immutable game state.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _highlighted_actions ( state: GameState ) -> frozenset [ Action ]:

        # Return no highlights for ordinary and drawn states.

        if state.outcome.status is not OutcomeStatus.WIN:

            # Return data to caller.

            return frozenset ()

        # Return data to caller.

        return frozenset (
            action
            for winning_line in state.outcome.winning_lines
            for action in winning_line
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _render_cell
    #
    # Description:
    #
    #   Format one board cell at a fixed width of three characters.
    #
    # Arguments:
    #
    #   mark        : Player mark assigned to the runtime player or board cell.
    #   highlighted : Highlighted supplied to the operation.
    #
    # Returns:
    #
    #   Text value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _render_cell ( mark: Mark, highlighted: bool ) -> str:

        # Highlight winning marks with parentheses.

        if highlighted:

            # Return data to caller.

            return f"({mark.value})"

        # Render empty cells as spaces and occupied cells as their mark.

        mark_text = mark.value if mark is not Mark.EMPTY else " "

        # Return data to caller.

        return f" {mark_text} "

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _border_characters
    #
    # Description:
    #
    #   Return Unicode or ASCII board-border text for the selected terminal mode.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _border_characters ( self ) -> tuple [ str, str, str, str ]:

        # Return Unicode borders when the output stream supports them.

        if self.use_unicode:

            # Return data to caller.

            return (
                "┌───┬───┬───┐",
                "├───┼───┼───┤",
                "└───┴───┴───┘",
                "│",
            )

        # Return data to caller.

        return (
            "+---+---+---+",
            "+---+---+---+",
            "+---+---+---+",
            "|",
        )
