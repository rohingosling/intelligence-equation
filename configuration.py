#-----------------------------------------------------------------------------------------------------------------------
# Module:  configuration.py
# Project: Intelligence Equation Tic-Tac-Toe
# Version: 2.0
# Author:  Rohin Gosling
#
# Description:
#
#   Loads UTF-8 YAML into immutable application configuration values and aggregates independent validation errors.
#
#-----------------------------------------------------------------------------------------------------------------------

from collections.abc import Mapping
from dataclasses     import dataclass
from pathlib         import Path
from types           import MappingProxyType

from yaml             import SafeLoader, YAMLError, load
from yaml.constructor import ConstructorError
from yaml.nodes       import MappingNode
from yaml.resolver    import BaseResolver

from domain.player                 import PlayerProfile, PlayerType
from errors                        import ConfigurationError
from intelligence.strategy_factory import StrategyFactory


SUPPORTED_CONFIGURATION_VERSION = 1.0


#-----------------------------------------------------------------------------------------------------------------------
# Class: ApplicationSettings
#
# Description:
#
#   Stores application-wide settings that affect runtime composition and reproducibility.
#
# Attributes:
#
#   random_seed : Optional seed controlling deterministic random choices.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class ApplicationSettings:

    random_seed: int | None = None


#-----------------------------------------------------------------------------------------------------------------------
# Class: MatchConfiguration
#
# Description:
#
#   Identifies the two configured profiles assigned to the X and O match slots.
#
# Attributes:
#
#   player_1_profile_id : Profile identifier assigned to Player 1.
#   player_2_profile_id : Profile identifier assigned to Player 2.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class MatchConfiguration:

    player_1_profile_id: str
    player_2_profile_id: str


#-----------------------------------------------------------------------------------------------------------------------
# Class: PresentationConfiguration
#
# Description:
#
#   Stores validated terminal-presentation settings for match output and replay.
#
# Attributes:
#
#   show_replay           : Whether the terminal output includes replay boards.
#   replay_boards_per_row : Maximum number of replay boards per row.
#   show_computer_scores  : Whether computer score tables are displayed.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class PresentationConfiguration:

    show_replay:           bool = True
    replay_boards_per_row: int  = 4
    show_computer_scores:  bool = False


#-----------------------------------------------------------------------------------------------------------------------
# Class: ApplicationConfiguration
#
# Description:
#
#   Provides one immutable validated configuration for application composition.
#
# Attributes:
#
#   version      : Supported YAML schema version.
#   application  : Validated application-wide settings.
#   profiles     : Immutable mapping of profile identifiers to player profiles.
#   match        : Selected player assignments for one match.
#   presentation : Validated terminal presentation settings.
#-----------------------------------------------------------------------------------------------------------------------

@dataclass ( frozen = True )
class ApplicationConfiguration:

    version:      float
    application:  ApplicationSettings
    profiles:     Mapping [ str, PlayerProfile ]
    match:        MatchConfiguration
    presentation: PresentationConfiguration

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

        # Protect the validated profile collection from runtime mutation.

        object.__setattr__ ( self, "profiles", MappingProxyType ( dict ( self.profiles ) ) )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: player_1_profile
    #
    # Description:
    #
    #   Player 1 profile.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Validated profile assigned to Player 1.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def player_1_profile ( self ) -> PlayerProfile:

        # Return data to caller.

        return self.profiles [ self.match.player_1_profile_id ]

    #-------------------------------------------------------------------------------------------------------------------
    # Function: player_2_profile
    #
    # Description:
    #
    #   Player 2 profile.
    #
    # Arguments:
    #
    #   None.
    #
    # Returns:
    #
    #   Validated profile assigned to Player 2.
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def player_2_profile ( self ) -> PlayerProfile:

        # Return data to caller.

        return self.profiles [ self.match.player_2_profile_id ]


#-----------------------------------------------------------------------------------------------------------------------
# Class: _UniqueKeySafeLoader
#
# Description:
#
#   Extends PyYAML safe loading with duplicate-key rejection.
#-----------------------------------------------------------------------------------------------------------------------

class _UniqueKeySafeLoader ( SafeLoader ):

    pass


#-----------------------------------------------------------------------------------------------------------------------
# Function: _construct_unique_mapping
#
# Description:
#
#   Construct one YAML mapping while rejecting duplicate keys that PyYAML would otherwise overwrite.
#
# Arguments:
#
#   loader : Loader supplied to the operation.
#   node   : Node supplied to the operation.
#   deep   : Deep supplied to the operation.
#
# Returns:
#
#   Return value produced by the operation.
#-----------------------------------------------------------------------------------------------------------------------

def _construct_unique_mapping (
    loader: _UniqueKeySafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict [ object, object ]:

    # Validate and construct each mapping entry.

    if not isinstance ( node, MappingNode ):
        raise ConstructorError ( None, None, "Expected a YAML mapping.", node.start_mark )

    # Initialize the mapping accumulator.

    mapping: dict [ object, object ] = {}

    # Construct each YAML key/value pair while checking for duplicates.

    for key_node, value_node in node.value:

        key = loader.construct_object ( key_node, deep = deep )

        # Check whether the YAML key is already present in the constructed mapping.

        try:
            duplicate_key = key in mapping

        except TypeError as error:

            # Raise the domain error for the invalid input.

            raise ConstructorError (
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from error

        # Reject duplicate YAML keys before the later value overwrites the earlier one.

        if duplicate_key:

            raise ConstructorError (
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )

        # Construct and store the YAML value after the key has passed validation.

        mapping [ key ] = loader.construct_object ( value_node, deep = deep )

    # Return data to caller.

    return mapping


_UniqueKeySafeLoader.add_constructor (
    BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


#-----------------------------------------------------------------------------------------------------------------------
# Class: ConfigurationLoader
#
# Description:
#
#   Reads and validates YAML before any runtime players or match engine are constructed.
#-----------------------------------------------------------------------------------------------------------------------

class ConfigurationLoader:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   strategy_factory : Factory used to construct configured strategies.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, strategy_factory: StrategyFactory ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        if not isinstance ( strategy_factory, StrategyFactory ):
            raise TypeError ( "ConfigurationLoader requires a StrategyFactory." )

        self.strategy_factory = strategy_factory

    #-------------------------------------------------------------------------------------------------------------------
    # Function: load
    #
    # Description:
    #
    #   Load and validate one YAML configuration document.
    #
    # Arguments:
    #
    #   configuration_path : YAML configuration file path.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def load ( self, configuration_path: str | Path ) -> ApplicationConfiguration:

        # Read and safely parse the requested YAML document.

        path = Path ( configuration_path )

        # Read the configuration file as UTF-8 text.

        try:
            configuration_text = path.read_text ( encoding = "utf-8" )

        except OSError as error:
            raise ConfigurationError ( f"Cannot read configuration '{path}': {error}" ) from error

        # Parse the YAML configuration with duplicate-key detection enabled.

        try:
            configuration_document = load (
                configuration_text,
                Loader = _UniqueKeySafeLoader,
            )

        except YAMLError as error:
            raise ConfigurationError ( f"Cannot parse configuration '{path}': {error}" ) from error

        # Validate and return the typed configuration.

        validator = _ConfigurationValidator ( self.strategy_factory )

        # Return data to caller.

        return validator.validate ( configuration_document )


#-----------------------------------------------------------------------------------------------------------------------
# Class: _ConfigurationValidator
#
# Description:
#
#   Validates one parsed YAML document while collecting independent schema and value failures.
#-----------------------------------------------------------------------------------------------------------------------

class _ConfigurationValidator:

    #-------------------------------------------------------------------------------------------------------------------
    # Function: __init__
    #
    # Description:
    #
    #   Initialize the instance with validated dependencies and configuration.
    #
    # Arguments:
    #
    #   strategy_factory : Factory used to construct configured strategies.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def __init__ ( self, strategy_factory: StrategyFactory ) -> None:

        # Initialize the instance with validated dependencies and configuration.

        self.strategy_factory = strategy_factory
        self.errors: list [ str ] = []

    #-------------------------------------------------------------------------------------------------------------------
    # Function: validate
    #
    # Description:
    #
    #   Validate one parsed configuration document.
    #
    # Arguments:
    #
    #   document : Document supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def validate ( self, document: object ) -> ApplicationConfiguration:

        # Validate the top-level document shape and fields.

        if not isinstance ( document, Mapping ):
            raise ConfigurationError ( "Configuration validation failed:\n- The YAML root must be a mapping." )

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping        = document,
            allowed_fields = frozenset ( { "version", "application", "profiles", "match", "presentation" } ),
            location       = "configuration",
        )

        # Prepare version for the next operation.

        version      = self._validate_version ( document.get ( "version" ) )
        application  = self._validate_application ( document.get ( "application", {} ) )
        profiles     = self._validate_profiles ( document.get ( "profiles" ) )
        match        = self._validate_match ( document.get ( "match" ), profiles )
        presentation = self._validate_presentation ( document.get ( "presentation", {} ) )

        # Report all accumulated validation errors together.

        if self.errors:
            error_list = "\n".join ( f"- {message}" for message in self.errors )
            raise ConfigurationError ( f"Configuration validation failed:\n{error_list}" )

        # Return data to caller.

        return ApplicationConfiguration (
            version      = version,
            application  = application,
            profiles     = profiles,
            match        = match,
            presentation = presentation,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_version
    #
    # Description:
    #
    #   Validate version.
    #
    # Arguments:
    #
    #   raw_version : Parsed YAML schema version.
    #
    # Returns:
    #
    #   Floating-point value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_version ( self, raw_version: object ) -> float:

        # Validate the required supported configuration version.

        if raw_version is None:
            self.errors.append ( "Missing required field 'version'." )

            return SUPPORTED_CONFIGURATION_VERSION

        # Reject values that do not satisfy the required type or range.

        if type ( raw_version ) is not float:
            self.errors.append ( "Field 'version' must be an x.y version number." )

            return SUPPORTED_CONFIGURATION_VERSION

        # Detect when raw version differs from the expected value.

        if raw_version != SUPPORTED_CONFIGURATION_VERSION:
            self.errors.append (
                f"Unsupported configuration version {raw_version}; expected {SUPPORTED_CONFIGURATION_VERSION}."
            )

        # Return data to caller.

        return raw_version

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_application
    #
    # Description:
    #
    #   Validate application.
    #
    # Arguments:
    #
    #   raw_application : Parsed YAML application-settings section.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_application ( self, raw_application: object ) -> ApplicationSettings:

        # Validate optional application settings.

        if not isinstance ( raw_application, Mapping ):
            self.errors.append ( "Field 'application' must be a mapping." )

            return ApplicationSettings ()

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping        = raw_application,
            allowed_fields = frozenset ( { "random_seed" } ),
            location       = "application",
        )

        # Read the optional random seed from the application settings.

        random_seed = raw_application.get ( "random_seed" )

        if "random_seed" in raw_application and random_seed is not None and type ( random_seed ) is not int:
            self.errors.append ( "Field 'application.random_seed' must be an integer." )
            random_seed = None

        # Return data to caller.

        return ApplicationSettings ( random_seed = random_seed )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_profiles
    #
    # Description:
    #
    #   Validate profiles.
    #
    # Arguments:
    #
    #   raw_profiles : Parsed YAML profile collection.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_profiles ( self, raw_profiles: object ) -> dict [ str, PlayerProfile ]:

        # Validate the required player-profile collection.

        if raw_profiles is None:
            self.errors.append ( "Missing required field 'profiles'." )

            return {}

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( raw_profiles, Mapping ):
            self.errors.append ( "Field 'profiles' must be a mapping." )

            return {}

        # Require at least one profile to be configured.

        if not raw_profiles:
            self.errors.append ( "Field 'profiles' must contain at least one profile." )

        # Initialize the profiles accumulator.

        profiles:         dict [ str, PlayerProfile ] = {}
        seen_profile_ids: set [ str ]                 = set ()

        # Validate each configured player profile.

        for raw_profile_id, raw_profile in raw_profiles.items ():

            # Reject profile identifiers that are not non-empty text.

            if not isinstance ( raw_profile_id, str ) or not raw_profile_id.strip ():
                self.errors.append ( "Every profile identifier must be non-empty text." )
                continue

            # Normalize the profile identifier before storing it.

            profile_id = raw_profile_id.strip ()

            # Reject profile identifiers that collide after normalization.

            if profile_id in seen_profile_ids:
                self.errors.append ( f"Profile identifier '{profile_id}' is duplicated after normalization." )
                continue

            # Remember the normalized profile identifier for duplicate detection.

            seen_profile_ids.add ( profile_id )
            profile = self._validate_profile ( profile_id, raw_profile )

            # Store successfully validated profiles by normalized identifier.

            if profile is not None:
                profiles [ profile_id ] = profile

        # Return data to caller.

        return profiles

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_profile
    #
    # Description:
    #
    #   Validate profile.
    #
    # Arguments:
    #
    #   profile_id  : Profile identifier from the YAML configuration.
    #   raw_profile : Parsed YAML player profile section.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_profile ( self, profile_id: str, raw_profile: object ) -> PlayerProfile | None:

        # Validate one human or computer profile schema.

        location = f"profiles.{profile_id}"

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( raw_profile, Mapping ):
            self.errors.append ( f"Field '{location}' must be a mapping." )

            return None

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping        = raw_profile,
            allowed_fields = frozenset ( { "type", "name", "intelligence" } ),
            location       = location,
        )

        # Read the required profile type and display name.

        player_type_text = self._required_text ( raw_profile, "type", location )
        player_name      = self._required_text ( raw_profile, "name", location )

        # Stop profile construction until both required text fields are valid.

        if player_type_text is None or player_name is None:
            return None

        # Normalize the profile type before enum conversion.

        normalized_player_type = player_type_text.lower ()

        # Reject normalized player type values outside the supported set.

        if normalized_player_type not in ( PlayerType.HUMAN.value, PlayerType.COMPUTER.value ):
            self.errors.append ( f"Field '{location}.type' must be 'human' or 'computer'." )

            return None

        # Convert the normalized profile type to the domain enum.

        player_type = PlayerType ( normalized_player_type )

        # Build human profiles separately because they do not use intelligence settings.

        if player_type is PlayerType.HUMAN:

            # Reject intelligence settings on human profiles.

            if "intelligence" in raw_profile:
                self.errors.append ( f"Human profile '{profile_id}' cannot contain intelligence settings." )

                return None

            # Return data to caller.

            return PlayerProfile (
                profile_id  = profile_id,
                name        = player_name,
                player_type = player_type,
            )

        # Validate the computer strategy configuration.

        intelligence_type, intelligence_parameters = self._validate_intelligence (
            profile_id       = profile_id,
            raw_intelligence = raw_profile.get ( "intelligence" ),
        )

        # Stop computer profile construction until intelligence settings validate.

        if intelligence_type is None or intelligence_parameters is None:
            return None

        # Return data to caller.

        return PlayerProfile (
            profile_id              = profile_id,
            name                    = player_name,
            player_type             = player_type,
            intelligence_type       = intelligence_type,
            intelligence_parameters = intelligence_parameters,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_intelligence
    #
    # Description:
    #
    #   Validate intelligence.
    #
    # Arguments:
    #
    #   profile_id       : Profile identifier from the YAML configuration.
    #   raw_intelligence : Parsed YAML intelligence-settings section.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_intelligence (
        self,
        profile_id: str,
        raw_intelligence: object,
    ) -> tuple [ str | None, dict [ str, object ] | None ]:

        # Validate one computer intelligence selection and its owned parameters.

        location = f"profiles.{profile_id}.intelligence"

        # Handle the missing raw intelligence value before continuing.

        if raw_intelligence is None:
            self.errors.append ( f"Computer profile '{profile_id}' requires field 'intelligence'." )

            return None, None

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( raw_intelligence, Mapping ):
            self.errors.append ( f"Field '{location}' must be a mapping." )

            return None, None

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping        = raw_intelligence,
            allowed_fields = frozenset ( { "type", "parameters" } ),
            location       = location,
        )

        # Read the required intelligence strategy name.

        intelligence_type = self._required_text ( raw_intelligence, "type", location )
        raw_parameters    = raw_intelligence.get ( "parameters", {} )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( raw_parameters, Mapping ):
            self.errors.append ( f"Field '{location}.parameters' must be a mapping." )

            return intelligence_type, None

        # Copy strategy parameters into an ordinary dictionary.

        parameters = dict ( raw_parameters )

        # Validate the strategy name when the required field was present.

        if intelligence_type is not None:

            normalized_intelligence_type = intelligence_type.lower ()

            try:
                self.strategy_factory.create ( normalized_intelligence_type, parameters )
            except ConfigurationError as error:
                self.errors.append ( f"Profile '{profile_id}': {error}" )

            intelligence_type = normalized_intelligence_type

        # Return data to caller.

        return intelligence_type, parameters

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_match
    #
    # Description:
    #
    #   Validate match.
    #
    # Arguments:
    #
    #   raw_match : Parsed YAML match section.
    #   profiles  : Profiles supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_match (
        self,
        raw_match: object,
        profiles: Mapping [ str, PlayerProfile ],
    ) -> MatchConfiguration:

        # Validate selected match profile references.

        if raw_match is None:

            self.errors.append ( "Missing required field 'match'." )

            return MatchConfiguration ( "", "" )

        # Reject values that do not satisfy the required type contract.

        if not isinstance ( raw_match, Mapping ):
            self.errors.append ( "Field 'match' must be a mapping." )

            return MatchConfiguration ( "", "" )

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping        = raw_match,
            allowed_fields = frozenset ( { "player_1", "player_2" } ),
            location       = "match",
        )

        # Read the two required match profile references.

        player_1_profile_id = self._required_text ( raw_match, "player_1", "match" )
        player_2_profile_id = self._required_text ( raw_match, "player_2", "match" )

        # Normalize the first match profile reference.

        normalized_player_1_profile_id = player_1_profile_id.strip () if player_1_profile_id else ""
        normalized_player_2_profile_id = player_2_profile_id.strip () if player_2_profile_id else ""

        # Validate each match-side profile reference.

        for field_name, profile_id in (
            ( "player_1", normalized_player_1_profile_id ),
            ( "player_2", normalized_player_2_profile_id ),
        ):
            if profile_id and profile_id not in profiles:
                self.errors.append (
                    f"Field 'match.{field_name}' references unknown profile '{profile_id}'."
                )

        # Return data to caller.

        return MatchConfiguration (
            player_1_profile_id = normalized_player_1_profile_id,
            player_2_profile_id = normalized_player_2_profile_id,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _validate_presentation
    #
    # Description:
    #
    #   Validate presentation.
    #
    # Arguments:
    #
    #   raw_presentation : Parsed YAML presentation section.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _validate_presentation ( self, raw_presentation: object ) -> PresentationConfiguration:

        # Validate optional presentation settings for later terminal composition.

        if not isinstance ( raw_presentation, Mapping ):
            self.errors.append ( "Field 'presentation' must be a mapping." )

            return PresentationConfiguration ()

        # Reject unsupported fields before validating the known fields.

        self._reject_unknown_fields (
            mapping = raw_presentation,
            allowed_fields = frozenset (
                { "show_replay", "replay_boards_per_row", "show_computer_scores" }
            ),
            location = "presentation",
        )

        # Read presentation options, applying defaults for omitted fields.

        show_replay           = raw_presentation.get ( "show_replay", True )
        replay_boards_per_row = raw_presentation.get ( "replay_boards_per_row", 4 )
        show_computer_scores  = raw_presentation.get ( "show_computer_scores", False )

        # Reject values that do not satisfy the required type or range.

        if type ( show_replay ) is not bool:
            self.errors.append ( "Field 'presentation.show_replay' must be a boolean." )
            show_replay = True

        # Reject values that do not satisfy the required type or range.

        if type ( replay_boards_per_row ) is not int or replay_boards_per_row < 1:
            self.errors.append ( "Field 'presentation.replay_boards_per_row' must be a positive integer." )
            replay_boards_per_row = 4

        # Reject non-boolean computer-score visibility flags.

        if type ( show_computer_scores ) is not bool:
            self.errors.append ( "Field 'presentation.show_computer_scores' must be a boolean." )
            show_computer_scores = False

        # Return data to caller.

        return PresentationConfiguration (
            show_replay           = show_replay,
            replay_boards_per_row = replay_boards_per_row,
            show_computer_scores  = show_computer_scores,
        )

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _required_text
    #
    # Description:
    #
    #   Required text.
    #
    # Arguments:
    #
    #   mapping    : Mapping whose fields are being validated.
    #   field_name : Field name supplied to the operation.
    #   location   : Location supplied to the operation.
    #
    # Returns:
    #
    #   Return value produced by the operation.
    #-------------------------------------------------------------------------------------------------------------------

    def _required_text (
        self,
        mapping: Mapping [ object, object ],
        field_name: str,
        location: str,
    ) -> str | None:

        # Validate one required non-empty text field.

        if field_name not in mapping:
            self.errors.append ( f"Missing required field '{location}.{field_name}'." )

            return None

        # Read the requested text field from the mapping.

        value = mapping [ field_name ]

        # Reject required text fields that are missing or blank.

        if not isinstance ( value, str ) or not value.strip ():

            self.errors.append ( f"Field '{location}.{field_name}' must be non-empty text." )

            return None

        # Return data to caller.

        return value.strip ()

    #-------------------------------------------------------------------------------------------------------------------
    # Function: _reject_unknown_fields
    #
    # Description:
    #
    #   Reject unknown fields.
    #
    # Arguments:
    #
    #   mapping        : Mapping whose fields are being validated.
    #   allowed_fields : Allowed fields supplied to the operation.
    #   location       : Location supplied to the operation.
    #
    # Returns:
    #
    #   None.
    #-------------------------------------------------------------------------------------------------------------------

    def _reject_unknown_fields (
        self,
        mapping: Mapping [ object, object ],
        allowed_fields: frozenset [ str ],
        location: str,
    ) -> None:

        # Reject every field not owned by the current schema location.

        for field_name in mapping:

            if field_name not in allowed_fields:

                self.errors.append ( f"Unknown field '{location}.{field_name}'." )
