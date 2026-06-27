#-----------------------------------------------------------------------------------------------------------------------
# Module:  __init__.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Exposes terminal interaction, board formatting, and immutable-history replay services.
#
#-----------------------------------------------------------------------------------------------------------------------

from presentation.board_renderer       import BoardRenderer
from presentation.replay_renderer      import ReplayRenderer
from presentation.score_table_renderer import ScoreTableRenderer
from presentation.terminal_interface   import TerminalInterface


__all__ = [
    "BoardRenderer",
    "ReplayRenderer",
    "ScoreTableRenderer",
    "TerminalInterface",
]
