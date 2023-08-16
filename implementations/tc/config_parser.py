from collections import defaultdict
from configparser import ConfigParser


class SilentConfigParser(ConfigParser):

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return defaultdict(lambda: None)