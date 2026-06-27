#-----------------------------------------------------------------------------------------------------------------------
# Module:  game_rules.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Implements the authoritative Tic-tac-toe rules, transitions, outcomes, utilities, and state validation.
#
#-----------------------------------------------------------------------------------------------------------------------

from functools import lru_cache

from domain.action     import Action
from domain.board      import Board
from domain.game_state import GameState
from domain.mark       import Mark
from domain.outcome    import Outcome, OutcomeStatus, WinningLine
from errors            import IllegalActionError, InvalidGameStateError, TerminalStateError

# Canonical board actions in row-major order.

CANONICAL_ACTIONS = tuple (
    Action ( row = row, column = column )
    for row in range ( 3 )
    for column in range ( 3 )
)

# All eight winning lines in rows, columns, and diagonals.

WINNING_LINES = (
    WinningLine ( actions = ( Action ( 0, 0 ), Action ( 0, 1 ), Action ( 0, 2 ) ) ),
    WinningLine ( actions = ( Action ( 1, 0 ), Action ( 1, 1 ), Action ( 1, 2 ) ) ),
    WinningLine ( actions = ( Action ( 2, 0 ), Action ( 2, 1 ), Action ( 2, 2 ) ) ),
    WinningLine ( actions = ( Action ( 0, 0 ), Action ( 1, 0 ), Action ( 2, 0 ) ) ),
    WinningLine ( actions = ( Action ( 0, 1 ), Action ( 1, 1 ), Action ( 2, 1 ) ) ),
    WinningLine ( actions = ( Action ( 0, 2 ), Action ( 1, 2 ), Action ( 2, 2 ) ) ),
    WinningLine ( actions = ( Action ( 0, 0 ), Action ( 1, 1 ), Action ( 2, 2 ) ) ),
    WinningLine ( actions = ( Action ( 0, 2 ), Action ( 1, 1 ), Action ( 2, 0 ) ) ),
)


#-----------------------------------------------------------------------------------------------------------------------
# Function: _winning_lines_for_board
#
# Description:
#
#   Find every winning line occupied by a playable mark on a board.
#
# Arguments:
#
#   board : Board to inspect.
#   mark  : Playable mark whose completed lines are requested.
#
# Returns:
#
#   Completed winning lines in canonical order.
#-----------------------------------------------------------------------------------------------------------------------

def _winning_lines_for_board ( board: Board, mark: Mark ) -> tuple [ WinningLine, ... ]:

    # Find every winning line occupied by a playable mark on a board.

    completed_lines = tuple (
        winning_line
        for winning_line in WINNING_LINES
        if all ( board.mark_at ( action ) is mark for action in winning_line )
    )

    # Return data to caller.

    return completed_lines


#-----------------------------------------------------------------------------------------------------------------------
# Function: _outcome_for_board
#
# Description:
#
#   Derive the canonical outcome for a structurally valid board.
#
# Arguments:
#
#   board : Board whose outcome is requested.
#
# Returns:
#
#   The canonical ongoing, draw, or winning outcome.
#-----------------------------------------------------------------------------------------------------------------------

def _outcome_for_board ( board: Board ) -> Outcome:

    # Derive the canonical outcome for a structurally valid board.

    # Find any winning line for X.

    winning_lines_x = _winning_lines_for_board ( board, Mark.X )

    if winning_lines_x:

        # Return data to caller.

        return Outcome.win ( winner = Mark.X, winning_lines = winning_lines_x )

    # Find any winning line for O.

    winning_lines_o = _winning_lines_for_board ( board, Mark.O )

    if winning_lines_o:

        # Return data to caller.

        return Outcome.win ( winner = Mark.O, winning_lines = winning_lines_o )

    # Treat a full board with no winner as a draw.

    if board.empty_count == 0:

        # Return data to caller.

        return Outcome.draw ()

    # Return data to caller.

    return Outcome.ongoing ()


#-----------------------------------------------------------------------------------------------------------------------
# Function: _is_reachable_board
#
# Description:
#
#   Determine whether a board can be reached from the empty board by alternating legal moves and stopping at terminal.
#
# Arguments:
#
#   board : Board to validate recursively.
#
# Returns:
#
#   True when at least one legal history reaches the board; otherwise False.
#-----------------------------------------------------------------------------------------------------------------------

@lru_cache ( maxsize = None )
def _is_reachable_board ( board: Board ) -> bool:

    # Determine whether a legal history can reach the board.

    mark_count_x = board.count ( Mark.X )
    mark_count_o = board.count ( Mark.O )

    if mark_count_x not in ( mark_count_o, mark_count_o + 1 ):

        # Return data to caller.

        return False

    if board.occupied_count == 0:

        # Return data to caller.

        return True

    last_mark = Mark.X if mark_count_x == mark_count_o + 1 else Mark.O

    # Search for a reachable non-terminal predecessor obtained by removing the last move.

    for cell_index, mark in enumerate ( board.cells ):

        if mark is not last_mark:
            continue

        # Recreate the predecessor board by removing the last played mark.

        predecessor_cells                = list ( board.cells )
        predecessor_cells [ cell_index ] = Mark.EMPTY
        predecessor_board                = Board ( cells = tuple ( predecessor_cells ) )

        if _outcome_for_board ( predecessor_board ).status is not OutcomeStatus.ONGOING:
            continue

        if _is_reachable_board ( predecessor_board ):

            # Return data to caller.

            return True

    # Return data to caller.

    return False


#-----------------------------------------------------------------------------------------------------------------------
# Function: _validate_game_state
#
# Description:
#
#   Validate one immutable game state and cache the result for repeated rule and search queries.
#
# Arguments:
#
#   state : Game state to validate.
#
# Returns:
#
#   None.
#-----------------------------------------------------------------------------------------------------------------------

@lru_cache ( maxsize = None )
def _validate_game_state ( state: GameState ) -> None:

    # Count marks to validate turn order and legal board shape.

    mark_count_x = state.board.count ( Mark.X )
    mark_count_o = state.board.count ( Mark.O )

    if mark_count_x not in ( mark_count_o, mark_count_o + 1 ):
        raise InvalidGameStateError ( "Board mark counts violate alternating turn order." )

    if state.move_number != mark_count_x + mark_count_o:
        raise InvalidGameStateError ( "Move number does not match the board mark counts." )

    # Prepare winning lines x for the next operation.

    winning_lines_x = _winning_lines_for_board ( state.board, Mark.X )
    winning_lines_o = _winning_lines_for_board ( state.board, Mark.O )

    if winning_lines_x and winning_lines_o:
        raise InvalidGameStateError ( "A legal Tic-tac-toe state cannot contain winners for both marks." )

    if winning_lines_x and mark_count_x != mark_count_o + 1:
        raise InvalidGameStateError ( "An X win requires X to have made the final move." )

    if winning_lines_o and mark_count_x != mark_count_o:
        raise InvalidGameStateError ( "An O win requires O to have made the final move." )

    if not _is_reachable_board ( state.board ):
        raise InvalidGameStateError ( "The board is not reachable by a legal history that stops at terminal." )

    # Recompute the board outcome and compare it with the stored state.

    expected_outcome = _outcome_for_board ( state.board )

    if state.outcome != expected_outcome:
        raise InvalidGameStateError ( "The stored outcome does not match the canonical board outcome." )


#-----------------------------------------------------------------------------------------------------------------------
# Function: _legal_actions_for_state
#
# Description:
#
#   Return cached canonical legal actions for one validated immutable state.
#
# Arguments:
#
#   state : Current immutable game state.
#
# Returns:
#
#   Return value produced by the operation.
#-----------------------------------------------------------------------------------------------------------------------

@lru_cache ( maxsize = None )
def _legal_actions_for_state ( state: GameState ) -> tuple [ Action, ... ]:

    # Legal actions for state.

    if state.is_terminal:

        # Return data to caller.

        return ()

    # Return data to caller.

    return tuple (
        action
        for action in CANONICAL_ACTIONS
        if state.board.mark_at ( action ) is Mark.EMPTY
    )


#-----------------------------------------------------------------------------------------------------------------------
# Function: _player_to_move_for_state
#
# Description:
#
#   Return the cached acting mark for one validated ongoing immutable state.
#
# Arguments:
#
#   state : Current immutable game state.
#
# Returns:
#
#   Return value produced by the operation.
#-----------------------------------------------------------------------------------------------------------------------

@lru_cache ( maxsize = None )
def _player_to_move_for_state ( state: GameState ) -> Mark:

    # Return data to caller.

    return Mark.X if state.board.count ( Mark.X ) == state.board.count ( Mark.O ) else Mark.O


#-----------------------------------------------------------------------------------------------------------------------
# Function: _apply_action_to_state
#
# Description:
#
#   Return the cached immutable successor for one validated state and legal action.
#
# Arguments:
#
#   state  : Current immutable game state.
#   action : Tic-tac-toe board coordinate or candidate action.
#
# Returns:
#
#   Return value produced by the operation.
#-----------------------------------------------------------------------------------------------------------------------

@lru_cache ( maxsize = None )
def _apply_action_to_state ( state: GameState, action: Action ) -> GameState:

    # Apply action to state.

    acting_mark     = _player_to_move_for_state ( state )
    successor_board = state.board.place ( action, acting_mark )
    successor_state = GameState (
        board       = successor_board,
        move_number = state.move_number + 1,
        outcome     = _outcome_for_board ( successor_board ),
    )
    _validate_game_state ( successor_state )

    # Return data to caller.

    return successor_state


#-----------------------------------------------------------------------------------------------------------------------
# Class: GameRules
#
# Description:
#
#   The stateless and authoritative Tic-tac-toe domain service.
#-----------------------------------------------------------------------------------------------------------------------

class GameRules:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: initial_state
    #
    # Description:
    #
    #   Create the empty initial game state.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   The validated initial state with X to move.
    #-------------------------------------------------------------------------------------------------------------------

    def initial_state ( self ) -> GameState:

        # Create the empty initial game state.

        initial_state = GameState (
            board       = Board.empty (),
            move_number = 0,
            outcome     = Outcome.ongoing (),
        )
        self.validate_state ( initial_state )

        # Return data to caller.

        return initial_state

    #-------------------------------------------------------------------------------------------------------------------
    # Function: legal_actions
    #
    # Description:
    #
    #   Return every legal action in canonical row-major order.
    #
    # Arguments:
    #
    #   state : Valid game state whose legal actions are requested.
    #
    # Returns:
    #
    #   Empty-cell actions for an ongoing state, or an empty tuple for a terminal state.
    #-------------------------------------------------------------------------------------------------------------------

    def legal_actions ( self, state: GameState ) -> tuple [ Action, ... ]:

        # Return every legal action in canonical row-major order.

        self.validate_state ( state )

        # Return data to caller.

        return _legal_actions_for_state ( state )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: player_to_move
    #
    # Description:
    #
    #   Derive the playable mark whose turn follows from the board counts.
    #
    # Arguments:
    #
    #   state : Valid ongoing game state.
    #
    # Returns:
    #
    #   Mark.X or Mark.O.
    #-------------------------------------------------------------------------------------------------------------------

    def player_to_move ( self, state: GameState ) -> Mark:

        # Derive the playable mark whose turn follows from the board counts.

        self.validate_state ( state )

        if state.is_terminal:
            raise TerminalStateError ( "A terminal game state has no player to move." )

        # Return data to caller.

        return _player_to_move_for_state ( state )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: apply_action
    #
    # Description:
    #
    #   Apply one legal action through the formal transition function and return a new immutable state.
    #
    # Arguments:
    #
    #   state  : Valid ongoing source state.
    #   action : Empty board coordinate selected by the current player.
    #
    # Returns:
    #
    #   The validated immutable successor state.
    #-------------------------------------------------------------------------------------------------------------------

    def apply_action ( self, state: GameState, action: Action ) -> GameState:

        # Apply one legal action through the formal transition function.

        self.validate_state ( state )

        # Reject moves or decisions after the game has already ended.

        if state.is_terminal:
            raise TerminalStateError ( "No action may be applied after the game reaches a terminal state." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( action, Action ):
            raise IllegalActionError ( "A game transition requires an Action coordinate." )

        # Reject actions targeting occupied cells.

        if state.board.mark_at ( action ) is not Mark.EMPTY:
            raise IllegalActionError ( f"Board coordinate {action} is already occupied." )

        # Return data to caller.

        return _apply_action_to_state ( state, action )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: winning_lines
    #
    # Description:
    #
    #   Return every completed winning line for a playable mark.
    #
    # Arguments:
    #
    #   state : Valid game state to inspect.
    #   mark  : Playable mark whose completed lines are requested.
    #
    # Returns:
    #
    #   Completed winning lines in canonical order.
    #-------------------------------------------------------------------------------------------------------------------

    def winning_lines ( self, state: GameState, mark: Mark ) -> tuple [ WinningLine, ... ]:

        # Return every completed winning line for a playable mark.

        self.validate_state ( state )

        if mark not in ( Mark.X, Mark.O ):
            raise ValueError ( "Winning lines may be requested only for X or O." )

        # Return data to caller.

        return _winning_lines_for_board ( state.board, mark )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: utility
    #
    # Description:
    #
    #   Evaluate a state from one playable mark's perspective.
    #
    # Arguments:
    #
    #   state       : Valid game state to evaluate.
    #   perspective : Playable mark whose utility is requested.
    #
    # Returns:
    #
    #   1 for a win, -1 for a loss, and 0 for an ongoing game or draw.
    #-------------------------------------------------------------------------------------------------------------------

    def utility ( self, state: GameState, perspective: Mark ) -> int:

        # Evaluate a state from one playable mark's perspective.

        self.validate_state ( state )

        # Reject perspective values outside the supported set.

        if perspective not in ( Mark.X, Mark.O ):
            raise ValueError ( "Utility may be evaluated only from X or O's perspective." )

        # Skip winner consistency checks when the game was not won.

        if state.outcome.status is not OutcomeStatus.WIN:

            # Return data to caller.

            return 0

        # Return data to caller.

        return 1 if state.outcome.winner is perspective else -1

    #-------------------------------------------------------------------------------------------------------------------
    # Function: validate_state
    #
    # Description:
    #
    #   Validate board counts, recursive reachability, terminal timing, move number, and canonical outcome details.
    #
    # Arguments:
    #
    #   state : Game state to validate.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def validate_state ( self, state: GameState ) -> None:

        # Validate every formal invariant of a game state.

        if not isinstance ( state, GameState ):
            raise InvalidGameStateError ( "Game rules require a GameState value." )

        _validate_game_state ( state )
