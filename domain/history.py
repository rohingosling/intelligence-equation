#-----------------------------------------------------------------------------------------------------------------------
# Module:  history.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines immutable accepted-move history and complete match-result values.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Iterator
from dataclasses     import dataclass

from domain.action     import Action
from domain.game_state import GameState
from domain.mark       import Mark
from domain.outcome    import Outcome, OutcomeStatus
from domain.player     import Player, PlayerDecision, PlayerType
from errors            import InvalidGameStateError


#-----------------------------------------------------------------------------------------------------------------------
# Class: MoveRecord
#
# Description:
#
#   An immutable record of one accepted move and its resulting game-state snapshot.
#
# Attributes:
#
#   move_number       : One-based accepted move number.
#   player_profile_id : Source profile identifier.
#   player_name       : Player display name at the time of the move.
#   player_type       : Human or computer control type.
#   mark              : Mark placed by the player.
#   action            : Accepted board coordinate.
#   state_after       : Immutable successor state.
#   decision          : Original player decision and optional diagnostics.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class MoveRecord:

    move_number:       int
    player_profile_id: str
    player_name:       str
    player_type:       PlayerType
    mark:              Mark
    action:            Action
    state_after:       GameState
    decision:          PlayerDecision

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate consistency between the move metadata, decision, and successor state.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __post_init__ ( self ) -> None:

        #-------------------------------------
        # Validate move identity and metadata.
        #-------------------------------------

        # Reject values that do not satisfy the required type or range.

        if type ( self.move_number ) is not int or not 1 <= self.move_number <= 9:
            raise InvalidGameStateError ( "Move records require a move number from 1 through 9." )

        # Reject move records without a profile identifier.

        if not isinstance ( self.player_profile_id, str ) or not self.player_profile_id:
            raise InvalidGameStateError ( "Move records require a player profile identifier." )

        # Reject move records without a player display name.

        if not isinstance ( self.player_name, str ) or not self.player_name:
            raise InvalidGameStateError ( "Move records require a player name." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.player_type, PlayerType ):
            raise InvalidGameStateError ( "Move records require a PlayerType value." )

        # Reject mark values outside the supported set.

        if self.mark not in ( Mark.X, Mark.O ):
            raise InvalidGameStateError ( "Move records require a playable mark." )

        # Reject move records with invalid action or decision objects.

        if not isinstance ( self.action, Action ) or not isinstance ( self.decision, PlayerDecision ):
            raise InvalidGameStateError ( "Move records require an action and its player decision." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.state_after, GameState ):
            raise InvalidGameStateError ( "Move records require an immutable successor state." )

        #-----------------------------------------
        # Validate the recorded transition result.
        #-----------------------------------------

        # Detect when state after.move number differs from the expected value.

        if self.state_after.move_number != self.move_number:
            raise InvalidGameStateError ( "Move number must match the successor state." )

        # Detect when decision.action differs from the expected value.

        if self.decision.action != self.action:
            raise InvalidGameStateError ( "The recorded action must match the player decision." )

        # Require the post-move board to contain the recorded mark at the recorded action.

        if self.state_after.board.mark_at ( self.action ) is not self.mark:
            raise InvalidGameStateError ( "The successor state must contain the recorded mark at the action." )


#-----------------------------------------------------------------------------------------------------------------------
# Class: GameHistory
#
# Description:
#
#   An immutable ordered collection containing accepted moves only.
#
# Attributes:
#
#   records : Accepted move records in play order.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class GameHistory:

    records: tuple [ MoveRecord, ... ] = ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate record types and contiguous move numbering.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __post_init__ ( self ) -> None:

        # Validate the immutable record sequence.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.records, tuple ):
            raise InvalidGameStateError ( "Game history records must be stored in an immutable tuple." )

        # Reject histories containing anything other than move records.

        if any ( not isinstance ( record, MoveRecord ) for record in self.records ):
            raise InvalidGameStateError ( "Game history may contain only MoveRecord values." )

        # Build the immutable expected move numbers collection.

        expected_move_numbers = tuple ( range ( 1, len ( self.records ) + 1 ) )
        actual_move_numbers   = tuple ( record.move_number for record in self.records )

        # Detect when actual move numbers differs from the expected value.

        if actual_move_numbers != expected_move_numbers:
            raise InvalidGameStateError ( "Game history move numbers must be contiguous and one-based." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: append
    #
    # Description:
    #
    #   Create a successor history containing one additional accepted move.
    #
    # Arguments:
    #
    #   record : Accepted move to append.
    #
    # Returns:
    #
    #   A new immutable game history.
    #-------------------------------------------------------------------------------------------------------------------

    def append ( self, record: MoveRecord ) -> "GameHistory":

        # Validate the next accepted move number.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( record, MoveRecord ):
            raise TypeError ( "Game history can append only a MoveRecord." )

        # Detect when record.move number differs from the expected value.

        if record.move_number != len ( self.records ) + 1:
            raise InvalidGameStateError ( "The appended move must follow the existing history." )

        # Return data to caller.

        return GameHistory ( records = self.records + ( record, ) )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __iter__
    #
    # Description:
    #
    #   Iterate over accepted moves in play order.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   An iterator over move records.
    #-------------------------------------------------------------------------------------------------------------------

    def __iter__ ( self ) -> Iterator [ MoveRecord ]:

        # Return data to caller.

        return iter ( self.records )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __len__
    #
    # Description:
    #
    #   Return the accepted move count.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Number of accepted move records.
    #-------------------------------------------------------------------------------------------------------------------

    def __len__ ( self ) -> int:

        # Return data to caller.

        return len ( self.records )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __getitem__
    #
    # Description:
    #
    #   Return one accepted move by zero-based history index.
    #
    # Arguments:
    #
    #   index : Zero-based history index.
    #
    # Returns:
    #
    #   The requested move record.
    #-------------------------------------------------------------------------------------------------------------------

    def __getitem__ ( self, index: int ) -> MoveRecord:

        # Return data to caller.

        return self.records [ index ]


#-----------------------------------------------------------------------------------------------------------------------
# Class: MatchResult
#
# Description:
#
#   An immutable completed-match result containing players, outcome, final state, and complete history.
#
# Attributes:
#
#   player_1    : Runtime player assigned to X.
#   player_2    : Runtime player assigned to O.
#   final_state : Terminal game-state snapshot.
#   outcome     : Canonical terminal outcome.
#   history     : Complete accepted-move history.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class MatchResult:

    player_1:    Player
    player_2:    Player
    final_state: GameState
    outcome:     Outcome
    history:     GameHistory

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Validate the completed match result.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __post_init__ ( self ) -> None:

        #-----------------------------
        # Validate player assignments.
        #-----------------------------

        # Reject match results without valid player objects.

        if not isinstance ( self.player_1, Player ) or not isinstance ( self.player_2, Player ):
            raise TypeError ( "Match results require two runtime players." )

        # Require match results to record X first and O second.

        if self.player_1.mark is not Mark.X or self.player_2.mark is not Mark.O:
            raise InvalidGameStateError ( "Player 1 must use X and Player 2 must use O." )

        #-----------------------------------------------------------
        # Validate terminal state, outcome, and history consistency.
        #-----------------------------------------------------------

        # Require match results to end with a terminal game state.

        if not isinstance ( self.final_state, GameState ) or not self.final_state.is_terminal:
            raise InvalidGameStateError ( "A match result requires a terminal final state." )

        # Require the match outcome to match the final game state.

        if not isinstance ( self.outcome, Outcome ) or self.outcome != self.final_state.outcome:
            raise InvalidGameStateError ( "Match outcome must equal the final-state outcome." )

        # Require match results to include a non-empty move history.

        if not isinstance ( self.history, GameHistory ) or not self.history.records:
            raise InvalidGameStateError ( "A match result requires a non-empty game history." )

        # Detect when history.records [ -1 ].state after differs from the expected value.

        if self.history.records [ -1 ].state_after != self.final_state:
            raise InvalidGameStateError ( "The last history snapshot must equal the final state." )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: player_x
    #
    # Description:
    #
    #   Return the runtime player assigned to X.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Player 1.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def player_x ( self ) -> Player:

        # Return data to caller.

        return self.player_1

    #-------------------------------------------------------------------------------------------------------------------
    # Function: player_o
    #
    # Description:
    #
    #   Return the runtime player assigned to O.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Player 2.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def player_o ( self ) -> Player:

        # Return data to caller.

        return self.player_2

    #-------------------------------------------------------------------------------------------------------------------
    # Function: winner
    #
    # Description:
    #
    #   Return the winning runtime player, or None for a draw.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   The winning player or None.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def winner ( self ) -> Player | None:

        # Resolve the winner from the canonical outcome.

        if self.outcome.status is not OutcomeStatus.WIN:

            # Return data to caller.

            return None

        # Return data to caller.

        return self.player_1 if self.outcome.winner is Mark.X else self.player_2
