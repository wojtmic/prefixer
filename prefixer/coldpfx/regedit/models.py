from dataclasses import dataclass
from typing import Optional

@dataclass
class RegistryNode:
    path: str
    """Registry path"""
    timestamp: int
    """Last modified timestamp"""
    values: dict[str, str]
    """Values of the node"""
    changed: bool = False
    """Whenever the node was modified or not"""

    def get(self, name: str) -> Optional[str]:
        return self.values.get(name)

    def set(self, name: str, value: str) -> Optional[str]:
        self.changed = True
        if value == '!prefixer_remove!': self.values.pop(name, None)
        self.values[name] = value

@dataclass
class RegistryHive:
    header: str
    """Registry string header"""
    relative: str
    """All strings relative to X wine comment"""
    nodes: dict[str, RegistryNode]
    """Nodes in the hive"""
    arch: str = 'win32'
    """Prefix architecture"""
