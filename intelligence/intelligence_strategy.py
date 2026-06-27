#-----------------------------------------------------------------------------------------------------------------------
# Module:  intelligence_strategy.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Defines immutable strategy diagnostics and the interchangeable computer-intelligence protocol.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from dataclasses     import dataclass, field
from math            import isfinite
from random          import Random
from types           import MappingProxyType
from typing          import Protocol, runtime_checkable

from domain.action     import Action
from domain.game_rules import GameRules
from domain.game_state import GameState
from domain.mark       import Mark
from errors            import StrategyContractError


#-----------------------------------------------------------------------------------------------------------------------
# Class: ActionScore
#
# Description:
#
#   An immutable strategy score and optional structured details for one candidate action.
#
# Attributes:
#
#   action  : Action.
#   score   : Score.
#   details : Details.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class ActionScore:

    action:  Action
    score:   int | float
    details: Mapping [ str, object ] = field ( default_factory = dict )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Finalize immutable value-object setup after dataclass initialization.
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

        # Validate and normalize the candidate score.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.action, Action ):
            raise TypeError ( "An action score requires an Action." )

        # Handle values where score, bool ) or not isinstance ( score, ( int has the expected float ) shape.

        if isinstance ( self.score, bool ) or not isinstance ( self.score, ( int, float ) ):
            raise TypeError ( "An action score requires a numeric value." )

        # Reject action scores that are not finite numeric values.

        if not isfinite ( float ( self.score ) ):
            raise ValueError ( "An action score must be finite." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.details, Mapping ):
            raise TypeError ( "Action-score details must be a mapping." )

        # Freeze score details so action scores remain immutable.

        object.__setattr__ ( self, "details", MappingProxyType ( dict ( self.details ) ) )


#-----------------------------------------------------------------------------------------------------------------------
# Class: StrategyDecision
#
# Description:
#
#   An immutable strategy selection with candidate scores and optional structured search metadata.
#
# Attributes:
#
#   action        : Action.
#   strategy_name : Strategy name.
#   action_scores : Action scores.
#   metadata      : Metadata.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class StrategyDecision:

    action:        Action
    strategy_name: str
    action_scores: tuple [ ActionScore, ... ] = ()
    metadata:      Mapping [ str, object ]    = field ( default_factory = dict )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __post_init__
    #
    # Description:
    #
    #   Finalize immutable value-object setup after dataclass initialization.
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

        # Validate and normalize the strategy decision.

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.action, Action ):
            raise TypeError ( "A strategy decision requires an Action." )

        # Reject strategy decisions without a non-empty strategy name.

        if not isinstance ( self.strategy_name, str ) or not self.strategy_name.strip ():
            raise ValueError ( "A strategy decision requires a strategy name." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.action_scores, tuple ):
            raise TypeError ( "Strategy action scores must be stored in an immutable tuple." )

        # Reject strategy decisions containing invalid action-score entries.

        if any ( not isinstance ( action_score, ActionScore ) for action_score in self.action_scores ):
            raise TypeError ( "Strategy decisions may contain only ActionScore values." )

        # Build the immutable scored actions collection.

        scored_actions = tuple ( action_score.action for action_score in self.action_scores )

        # Detect when len ( scored actions ) differs from the expected value.

        if len ( scored_actions ) != len ( set ( scored_actions ) ):
            raise ValueError ( "A strategy decision cannot score one action more than once." )

        # Require the selected action to appear in the scored action list.

        if self.action_scores and self.action not in scored_actions:
            raise ValueError ( "The selected action must be present in the candidate action scores." )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( self.metadata, Mapping ):
            raise TypeError ( "Strategy-decision metadata must be a mapping." )

        # Normalize immutable decision metadata after validation.

        object.__setattr__ ( self, "strategy_name", self.strategy_name.strip () )
        object.__setattr__ ( self, "metadata", MappingProxyType ( dict ( self.metadata ) ) )


#-----------------------------------------------------------------------------------------------------------------------
# Class: IntelligenceStrategy
#
# Description:
#
#   Structural contract implemented by every interchangeable computer-intelligence strategy.
#-----------------------------------------------------------------------------------------------------------------------

@runtime_checkable
class IntelligenceStrategy ( Protocol ):

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

        # Return the public strategy name.

        ...

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

        # Select one legal action according to the strategy contract.

        ...


#-----------------------------------------------------------------------------------------------------------------------
# Function: validate_strategy_request
#
# Description:
#
#   Enforce the common strategy-input contract against the authoritative game-rule service.
#
# Arguments:
#
#   game_rules       : Authoritative Tic-tac-toe rule service.
#   state            : Current immutable game state.
#   acting_mark      : Mark assigned to the strategy for the current decision.
#   legal_actions    : Canonical legal actions available in the current state.
#   random_generator : Shared random-number generator for stochastic choices.
#
# Returns:
#
#   None.
#-----------------------------------------------------------------------------------------------------------------------

def validate_strategy_request (
    game_rules: GameRules,
    state: GameState,
    acting_mark: Mark,
    legal_actions: tuple [ Action, ... ],
    random_generator: Random,
) -> None:

    # Validate shared strategy dependencies and current-state values.

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( game_rules, GameRules ):
        raise TypeError ( "Strategy validation requires a GameRules service." )

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( state, GameState ):
        raise StrategyContractError ( "Strategies require an immutable GameState." )

    # Validate the supplied game state against the game rules.

    game_rules.validate_state ( state )

    # Reject moves or decisions after the game has already ended.

    if state.is_terminal:
        raise StrategyContractError ( "Strategies cannot select an action from a terminal state." )

    # Reject acting mark values outside the supported set.

    if acting_mark not in ( Mark.X, Mark.O ):
        raise StrategyContractError ( "Strategies require a playable acting mark." )

    # Reject strategy requests for a mark that is not next to move.

    if acting_mark is not game_rules.player_to_move ( state ):
        raise StrategyContractError ( "The acting mark does not match the state player to move." )

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( legal_actions, tuple ):
        raise StrategyContractError ( "Legal actions must be supplied as an immutable tuple." )

    # Detect when legal actions differs from the expected value.

    if legal_actions != game_rules.legal_actions ( state ):
        raise StrategyContractError ( "The supplied legal actions do not match the game rules." )

    # Reject strategy requests that have no legal actions available.

    if not legal_actions:
        raise StrategyContractError ( "An ongoing state must provide at least one legal action." )

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( random_generator, Random ):
        raise StrategyContractError ( "Strategies require an injected random-number generator." )


#-----------------------------------------------------------------------------------------------------------------------
# Function: validate_strategy_decision
#
# Description:
#
#   Enforce the strategy-output contract before a computer player returns a domain player decision.
#
# Arguments:
#
#   decision      : Strategy or player decision returned by the caller.
#   strategy_name : Registered strategy name from configuration.
#   legal_actions : Canonical legal actions available in the current state.
#
# Returns:
#
#   None.
#-----------------------------------------------------------------------------------------------------------------------

def validate_strategy_decision (
    decision: StrategyDecision,
    strategy_name: str,
    legal_actions: tuple [ Action, ... ],
) -> None:

    # Validate the returned decision and every diagnostic candidate action.

    # Reject values that do not satisfy the required type contract.

    if not isinstance ( decision, StrategyDecision ):
        raise StrategyContractError ( f"Strategy {strategy_name} did not return a StrategyDecision." )

    # Detect when decision.strategy name differs from the expected value.

    if decision.strategy_name != strategy_name:
        raise StrategyContractError ( "Strategy decision name does not match the active strategy." )

    # Reject decisions that choose an illegal action.

    if decision.action not in legal_actions:
        raise StrategyContractError ( f"Strategy {strategy_name} selected illegal action {decision.action}." )

    # Reject diagnostics that score illegal actions.

    if any ( action_score.action not in legal_actions for action_score in decision.action_scores ):
        raise StrategyContractError ( f"Strategy {strategy_name} scored an illegal candidate action." )
