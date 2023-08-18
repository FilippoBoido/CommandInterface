from config_parser import SilentConfigParser
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ConsoleArgs:
    ams_net_id: str
    path_config: str


@dataclass
class Paths:
    path_to_config_file: str = ''

    conf_file_path_section: ClassVar[str] = 'app.paths'
    conf_file_ignore_ads_symbols: ClassVar[str] = 'ignore_ads_symbols'
    conf_file_symbol_hints: ClassVar[str] = 'symbol_hints'
    conf_file_watchlist: ClassVar[str] = 'watchlist'
    conf_file_notification_symbols: ClassVar[str] = 'notification_symbols'
    conf_file_ads_notifications: ClassVar[str] = 'ads_notifications'
    conf_file_rpc_definitions: ClassVar[str] = 'rpc_definitions'
    conf_file_session_history: ClassVar[str] = 'session_history'
    conf_file_recipe: ClassVar[str] = 'recipe'

    default_recipe_file_path: ClassVar[str] = 'recipe.json'
    default_session_history_file_path: ClassVar[str] = 'session_history.txt'
    default_rpc_definitions_file_path: ClassVar[str] = 'rpc_definitions.json'
    default_ignore_ads_symbols_file_path: ClassVar[str] = 'ignore_ads_symbols.txt'
    default_symbol_hints_file_path: ClassVar[str] = 'symbol_hint_file.txt'
    default_watchlist_file_path: ClassVar[str] = 'watchlist.txt'
    default_notification_symbols_file_path: ClassVar[str] = 'notification_list.txt'
    default_ads_notifications_file_path: ClassVar[str] = 'ads_notifications.csv'
    default_config_file_path: ClassVar[str] = 'config.ini'

    def __post_init__(self):

        config = SilentConfigParser()
        config.read(self.path_to_config_file)

        self.recipe_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_recipe],
            self.default_recipe_file_path)

        self.session_history_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_session_history],
            self.default_session_history_file_path)

        self.rpc_definitions_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_rpc_definitions],
            self.default_rpc_definitions_file_path)

        self.ignore_ads_symbols_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_ignore_ads_symbols],
            self.default_ignore_ads_symbols_file_path)

        self.symbol_hints_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_symbol_hints],
            self.default_symbol_hints_file_path)

        self.watchlist_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_watchlist],
            self.default_watchlist_file_path)

        self.notification_symbols_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_notification_symbols],
            self.default_notification_symbols_file_path)

        self.ads_notifications_file_path = self._set_file_path(
            config[Paths.conf_file_path_section][Paths.conf_file_ads_notifications],
            self.default_ads_notifications_file_path)

    @staticmethod
    def _set_file_path(config_file_path: str, default_file_path: str) -> str:
        return default_file_path if not config_file_path else config_file_path

    @staticmethod
    def write_default_config_file():
        config = SilentConfigParser()
        config[Paths.conf_file_path_section] = {
            Paths.conf_file_ignore_ads_symbols: Paths.default_ignore_ads_symbols_file_path,
            Paths.conf_file_symbol_hints: Paths.default_symbol_hints_file_path,
            Paths.conf_file_watchlist: Paths.default_watchlist_file_path,
            Paths.conf_file_notification_symbols: Paths.default_notification_symbols_file_path,
            Paths.conf_file_ads_notifications: Paths.default_ads_notifications_file_path,
            Paths.conf_file_rpc_definitions: Paths.default_rpc_definitions_file_path,
            Paths.conf_file_session_history: Paths.default_session_history_file_path,
            Paths.conf_file_recipe:Paths.default_recipe_file_path
        }
        with open(Paths.default_config_file_path, 'w') as configfile:
            config.write(configfile)
