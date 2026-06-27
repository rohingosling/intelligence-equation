#-----------------------------------------------------------------------------------------------------------------------
# Module:  player.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Exposes the runtime player and player-decision contracts for concrete player implementations.
#
#-----------------------------------------------------------------------------------------------------------------------

from domain.player import Player, PlayerDecision


__all__ = [
    "Player",
    "PlayerDecision",
]
