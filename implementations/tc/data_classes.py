from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ConsoleArgs:
    ams_net_id: str
    path_config: str


@dataclass
class Paths:
    ignore_ads_symbols_file_path: str = ''
    symbol_hints_file_path: str = ''
    watchlist_file_path: str = ''
    notification_symbols_file_path: str = ''
    ads_notifications_file_path: str = ''

    conf_file_path_section: ClassVar[str] = 'app.paths'
    conf_file_ignore_ads_symbols: ClassVar[str] = 'ignore_ads_symbols'
    conf_file_symbol_hints: ClassVar[str] = 'symbol_hints'
    conf_file_watchlist: ClassVar[str] = 'watchlist'
    conf_file_notification_symbols: ClassVar[str] = 'notification_symbols'
    conf_file_ads_notifications: ClassVar[str] = 'ads_notifications'

    default_ignore_ads_symbols_file_path: ClassVar[str] = 'ignore_ads_symbols.txt'
    default_symbol_hints_file_path: ClassVar[str] = 'symbol_hint_file.txt'
    default_watchlist_file_path: ClassVar[str] = 'watchlist.txt'
    default_notification_symbols_file_path: ClassVar[str] = 'notification_list.txt'
    default_ads_notifications_file_path: ClassVar[str] = 'ADSNotifications.txt'

    def __post_init__(self):
        self.ignore_ads_symbols_file_path = self.set_file_path(self.ignore_ads_symbols_file_path,
                                                               self.default_ignore_ads_symbols_file_path)
        self.symbol_hints_file_path = self.set_file_path(self.symbol_hints_file_path,
                                                         self.default_symbol_hints_file_path)
        self.watchlist_file_path = self.set_file_path(self.watchlist_file_path,
                                                      self.default_watchlist_file_path)
        self.notification_symbols_file_path = self.set_file_path(self.notification_symbols_file_path,
                                                                 self.default_notification_symbols_file_path)
        self.ads_notifications_file_path = self.set_file_path(self.ads_notifications_file_path,
                                                              self.default_ads_notifications_file_path)

    @staticmethod
    def set_file_path(config_file_path: str, default_file_path: str) -> str:
        return default_file_path if not config_file_path else config_file_path
