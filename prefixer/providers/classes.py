from pathlib import Path
from abc import ABC, abstractmethod

provider_reg: dict[str, type['PrefixProvider']] = {}

class Prefix(ABC):
    def __init__(self, pfx_path: Path, files_path: Path, binary_path: Path):
        self.pfx_path:    Path = pfx_path
        self.files_path:  Path = files_path
        self.binary_path: Path = binary_path

    @abstractmethod
    def run(self, exe: Path, args: list[str] = None, silent: bool = False):
        """Runs an exe file in the prefix"""
        pass

class PrefixProvider(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        provider_reg[cls.__name__] = cls

    @abstractmethod
    def get_prefixes(self) -> dict[str, str]:
        """Returns a list of prefix names mapped to IDs"""
        pass

    @abstractmethod
    def get_prefix(self, id: str) -> Prefix:
        """Returns a Prefix instance"""
        pass

    def get_all_prefixes(self, name: str) -> list[Prefix]:
        """Returns a list of all prefix objects; very slow"""
        returns = []
        for p in self.get_prefixes():
            returns.append(self.get_prefix(p))

        return returns
