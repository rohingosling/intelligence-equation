#-----------------------------------------------------------------------------------------------------------------------
# Module:  strategy_factory.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Registers and constructs validated interchangeable computer-intelligence strategies.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Callable, Mapping

from domain.game_rules import GameRules
from errors            import ConfigurationError, StrategyContractError
from intelligence.causal_entropy_strategy import (
    DEFAULT_HORIZON, DEFAULT_TEMPERATURE, CausalEntropyStrategy,
)
from intelligence.intelligence_strategy import IntelligenceStrategy
from intelligence.minimax_strategy      import MinimaxStrategy
from intelligence.random_strategy       import RandomStrategy
from intelligence.tactical_strategy     import TacticalStrategy


StrategyConstructor = Callable [ [ GameRules, Mapping [ str, object ] ], IntelligenceStrategy ]


#-----------------------------------------------------------------------------------------------------------------------
# Class: StrategyFactory
#
# Description:
#
#   Owns the central strategy registry and constructs validated strategies from configuration-style parameters.
#-----------------------------------------------------------------------------------------------------------------------

class StrategyFactory:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, game_rules: GameRules ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        if not isinstance ( game_rules, GameRules ):
            raise TypeError ( "StrategyFactory requires a GameRules service." )

        # Store the validated strategy dependencies.

        self.game_rules = game_rules
        self._constructors: dict [ str, StrategyConstructor ] = {}

        # Register the built-in strategy constructors.

        self.register ( RandomStrategy.NAME, self._construct_random )
        self.register ( TacticalStrategy.NAME, self._construct_tactical )
        self.register ( MinimaxStrategy.NAME, self._construct_minimax )
        self.register ( CausalEntropyStrategy.NAME, self._construct_causal_entropy )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: registered_names
    #
    # Description:
    #
    #   Return the supported strategy names in registration order.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Tuple of registered public strategy names.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def registered_names ( self ) -> tuple [ str, ... ]:

        # Return data to caller.

        return tuple ( self._constructors )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: register
    #
    # Description:
    #
    #   Register one strategy constructor under its public name.
    #
    # Arguments:
    #
    #   strategy_name : Registered strategy name from configuration.
    #   constructor   : Constructor supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def register ( self, strategy_name: str, constructor: StrategyConstructor ) -> None:

        # Validate and register one strategy constructor.

        # Reject strategy names that are not non-empty text.

        if not isinstance ( strategy_name, str ) or not strategy_name.strip ():
            raise ValueError ( "Strategy registration requires a non-empty name." )

        # Reject strategy constructors that are not callable.

        if not callable ( constructor ):
            raise TypeError ( "Strategy registration requires a callable constructor." )

        # Normalize the strategy name for lookup and registration.

        normalized_name = strategy_name.strip ().lower ()

        if normalized_name in self._constructors:
            raise ValueError ( f"Strategy '{normalized_name}' is already registered." )

        # Store the constructor under its normalized strategy name.

        self._constructors [ normalized_name ] = constructor

    #-------------------------------------------------------------------------------------------------------------------
    # Function: create
    #
    # Description:
    #
    #   Create one runtime player or strategy from validated configuration.
    #
    # Arguments:
    #
    #   strategy_name : Registered strategy name from configuration.
    #   parameters    : Parameters supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def create (
        self,
        strategy_name: str,
        parameters: Mapping [ str, object ] | None = None,
    ) -> IntelligenceStrategy:

        # Resolve and construct the requested strategy.

        # Reject strategy names that are not non-empty text.

        if not isinstance ( strategy_name, str ) or not strategy_name.strip ():
            raise ConfigurationError ( "A computer profile requires an intelligence strategy name." )

        # Handle the missing parameters value before continuing.

        if parameters is None:
            parameters = {}

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( parameters, Mapping ):
            raise ConfigurationError ( "Intelligence strategy parameters must be a mapping." )

        # Normalize the strategy name for lookup and registration.

        normalized_name = strategy_name.strip ().lower ()
        constructor     = self._constructors.get ( normalized_name )

        # Handle the missing constructor value before continuing.

        if constructor is None:
            raise ConfigurationError ( f"Unknown intelligence strategy '{normalized_name}'." )

        # Construct the requested strategy from the normalized registration.

        strategy = constructor ( self.game_rules, parameters )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( strategy, IntelligenceStrategy ):
            raise StrategyContractError ( f"Registered constructor '{normalized_name}' returned an invalid strategy." )

        # Detect when strategy.name differs from the expected value.

        if strategy.name != normalized_name:
            raise StrategyContractError ( "Constructed strategy name does not match its factory registration." )

        # Return data to caller.

        return strategy

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _construct_random
    #
    # Description:
    #
    #   Construct random.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #   parameters : Parameters supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _construct_random (
        game_rules: GameRules,
        parameters: Mapping [ str, object ],
    ) -> IntelligenceStrategy:

        # Construct random.

        StrategyFactory._reject_unknown_parameters ( RandomStrategy.NAME, parameters, frozenset () )

        # Return data to caller.

        return RandomStrategy ( game_rules )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _construct_tactical
    #
    # Description:
    #
    #   Construct tactical.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #   parameters : Parameters supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _construct_tactical (
        game_rules: GameRules,
        parameters: Mapping [ str, object ],
    ) -> IntelligenceStrategy:

        # Reject parameters not owned by the selected strategy.

        StrategyFactory._reject_unknown_parameters (
            TacticalStrategy.NAME,
            parameters,
            frozenset ( { "tie_breaker" } ),
        )

        # Translate tactical parameter errors into configuration errors.

        try:

            # Return data to caller.

            return TacticalStrategy (
                game_rules  = game_rules,
                tie_breaker = parameters.get ( "tie_breaker" ),
            )

        except ValueError as error:

            raise ConfigurationError ( f"Invalid tactical strategy parameters: {error}" ) from error

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _construct_minimax
    #
    # Description:
    #
    #   Construct minimax.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #   parameters : Parameters supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _construct_minimax (
        game_rules: GameRules,
        parameters: Mapping [ str, object ],
    ) -> IntelligenceStrategy:

        # Construct minimax.

        StrategyFactory._reject_unknown_parameters (
            MinimaxStrategy.NAME,
            parameters,
            frozenset ( { "tie_breaker" } ),
        )

        # Translate minimax parameter errors into configuration errors.

        try:

            # Return data to caller.

            return MinimaxStrategy (
                game_rules  = game_rules,
                tie_breaker = parameters.get ( "tie_breaker" ),
            )

        except ValueError as error:
            raise ConfigurationError ( f"Invalid minimax strategy parameters: {error}" ) from error

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _construct_causal_entropy
    #
    # Description:
    #
    #   Construct causal entropy.
    #
    # Arguments:
    #
    #   game_rules : Authoritative Tic-tac-toe rule service.
    #   parameters : Parameters supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _construct_causal_entropy (
        game_rules: GameRules,
        parameters: Mapping [ str, object ],
    ) -> IntelligenceStrategy:

        # Construct causal entropy.

        StrategyFactory._reject_unknown_parameters (
            CausalEntropyStrategy.NAME,
            parameters,
            frozenset ( { "horizon", "temperature", "tie_breaker" } ),
        )

        # Translate causal-entropy parameter errors into configuration errors.

        try:

            # Return data to caller.

            return CausalEntropyStrategy (
                game_rules  = game_rules,
                horizon     = parameters.get ( "horizon", DEFAULT_HORIZON ),
                temperature = parameters.get ( "temperature", DEFAULT_TEMPERATURE ),
                tie_breaker = parameters.get ( "tie_breaker" ),
            )
        except ValueError as error:
            raise ConfigurationError ( f"Invalid causal_entropy strategy parameters: {error}" ) from error

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _reject_unknown_parameters
    #
    # Description:
    #
    #   Reject unknown parameters.
    #
    # Arguments:
    #
    #   strategy_name      : Registered strategy name from configuration.
    #   parameters         : Parameters supplied to the operation.
    #   allowed_parameters : Allowed parameters supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _reject_unknown_parameters (
        strategy_name: str,
        parameters: Mapping [ str, object ],
        allowed_parameters: frozenset [ str ],
    ) -> None:

        # Build the immutable unknown parameters collection.

        unknown_parameters = tuple (
            parameter_name
            for parameter_name in parameters
            if parameter_name not in allowed_parameters
        )

        # Report any unsupported strategy parameters together.

        if unknown_parameters:
            parameter_list = ", ".join ( sorted ( str ( name ) for name in unknown_parameters ) )
            raise ConfigurationError (
                f"Unknown {strategy_name} strategy parameter(s): {parameter_list}."
            )
