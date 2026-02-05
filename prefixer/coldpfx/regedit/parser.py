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
    current_key = None
    arch = None

    for line in hive_raw:
        clean_line = line.strip()

        if clean_line.startswith('#arch='):
            arch = clean_line.split('=')[1].strip()
            continue

        node_match = node_header_pattern.match(clean_line)
        if node_match:
            key_path = node_match.group('key_path')
            timestamp = int(node_match.group('timestamp'))
            node = RegistryNode(key_path, timestamp, {})
            nodes[key_path] = node
            continue

        if node:
            if line.startswith("  ") and current_key:
                new_val = node.values[current_key] + "\n" + line.rstrip()
                node.values[current_key] = new_val
                continue

            value_match = value_pattern.match(clean_line)
            if value_match:
                if value_match.group('default'):
                    key = '@'
                else:
                    key = value_match.group('key').replace(r'\"', '"').replace(r'\\', '\\')

                current_key = key
                node.set(key, value_match.group('value'))
                node.changed = False
                continue

    if not arch: arch = 'win64'
    return RegistryHive(header, relative, nodes, arch)

def parse_hive_file(path: str):
    """Helper to read and redirect to parse_hive"""
    with open(path, 'r') as f:
        return parse_hive(f.readlines())
