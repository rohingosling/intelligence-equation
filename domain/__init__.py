#-----------------------------------------------------------------------------------------------------------------------
# Module:  __init__.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Exposes the authoritative immutable game model, match engine, player contracts, and history values.
#
#-----------------------------------------------------------------------------------------------------------------------

from domain.action     import Action
from domain.board      import Board
from domain.game       import Game, GameObserver
from domain.game_rules import CANONICAL_ACTIONS, WINNING_LINES, GameRules
from domain.game_state import GameState
from domain.history    import GameHistory, MatchResult, MoveRecord
from domain.mark       import Mark
from domain.outcome    import Outcome, OutcomeStatus, WinningLine
from domain.player     import Player, PlayerDecision, PlayerProfile, PlayerType


__all__ = [
    "Action",
    "Board",
    "CANONICAL_ACTIONS",
    "Game",
    "GameHistory",
    "GameObserver",
    "GameRules",
    "GameState",
    "Mark",
    "MatchResult",
    "MoveRecord",
    "Outcome",
    "OutcomeStatus",
    "Player",
    "PlayerDecision",
    "PlayerProfile",
    "PlayerType",
    "WINNING_LINES",
    "WinningLine",
]
