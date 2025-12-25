from prefixer.coldpfx.regedit.models import RegistryNode, RegistryHive
from typing import List
import re

def parse_hive(hive_raw: List[str]):
    """Parses raw strings of a hive into a RegistryHive object"""
    header = hive_raw[0].strip()
    relative = hive_raw[1].strip()
    node_header_pattern = re.compile(r'^\[(?P<key_path>.+)\]\s+(?P<timestamp>\d+)$')
    value_pattern = re.compile(r'^(?:"(?P<key>(?:[^"\\]|\\.)*)"|(?P<default>@))=(?P<value>.*)$')

    node = None
    nodes = {}
    arch = 'win32'

    for line in hive_raw:
        line = line.strip()

        if line.startswith('#arch='):
            arch = line.split('=')[1].strip()
            continue

        node_match = node_header_pattern.match(line)

        if node_match:
            key_path = node_match.group('key_path')
            timestamp = int(node_match.group('timestamp'))

            node = RegistryNode(key_path, timestamp, {})
            nodes[key_path] = node
            continue

        if node:
            value_match = value_pattern.match(line)
            if value_match:
                if value_match.group('default'):
                    key = '@'
                else:
                    key = value_match.group('key').replace(r'\"', '"').replace(r'\\', '\\')

                value = value_match.group('value')
                node.set(key, value)
                node.changed = False
                continue

    return RegistryHive(header, relative, nodes, arch)

def parse_hive_file(path: str):
    """Helper to read and redirect to parse_hive"""
    with open(path, 'r') as f:
        return parse_hive(f.readlines())
