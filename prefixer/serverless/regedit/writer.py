from prefixer.serverless.regedit.models import RegistryHive
import time
from typing import List

def serialize(hive: RegistryHive) -> List[str]:
    lines = [hive.header, ";; All keys relative to REGISTRY\\\\User\\\\S-1-5-21-1408259311-2033730227-1000-1000", '', f'#arch={hive.arch}', '']

    current_time = int(time.time())

    for key_path, node in sorted(hive.nodes.items()):
        if not node.values:
            continue

        if node.changed: lines.append(f'[{node.path}] {current_time}')
        else: lines.append(f'[{node.path}] {node.timestamp}')

        for name, raw_value in sorted(node.values.items()):
            if name == '@':
                lines.append(f'@={raw_value}')
            else:
                escaped_name = name.replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'"{escaped_name}"={raw_value}')

        lines.append("")

    return lines

def write_to_file(hive: RegistryHive, path: str):
    with open(path, 'w') as f:
        data = serialize(hive)
        f.write('\n'.join(data))
