import vdf
import os
import sys
from .exceptions import NoSteamError, NoProtonError

LIBMANIFEST_LOCATION = os.path.expanduser('~/.steam/steam/steamapps/libraryfolders.vdf')

def get_libraries():
    if not os.path.exists(LIBMANIFEST_LOCATION):
        raise NoSteamError

    with open(LIBMANIFEST_LOCATION, 'r') as f:
        libmanifest = vdf.loads(f.read())

    libs = []
    for lib in libmanifest['libraryfolders']:
        if not os.path.exists(libmanifest['libraryfolders'][lib]['path']): continue
        libs.append(lib)

    libPaths = []
    for lib in libs:
        libPaths.append(libmanifest['libraryfolders'][lib]['path'])

    libApps = []
    for lib in libs:
        libApps.append(libmanifest['libraryfolders'][lib]['apps'])

    return libPaths, libApps

def get_prefix_path(targetId):
    libs = get_libraries()
    libPaths = libs[0]
    apps = libs[1]

    index = next((i for i, app in enumerate(apps) if targetId in app), None)
    if index is None:
        return None

    path = f'{libPaths[index]}/steamapps/compatdata/{targetId}/pfx'
    return path

def get_manifest(targetId):
    libs = get_libraries()
    libPaths = libs[0]
    apps = libs[1]

    index = next((i for i, app in enumerate(apps) if targetId in app), None)
    if index is None:
        return None

    path = f'{libPaths[index]}/steamapps/appmanifest_{targetId}.acf'
    with open(path, 'r') as f:
        manifestData = vdf.loads(f.read())

    return manifestData

def get_installdir(targetId):
    manifest = get_manifest(targetId)
    libs = get_libraries()
    libPaths = libs[0]
    apps = libs[1]

    index = next((i for i, app in enumerate(apps) if targetId in app), None)
    if index is None:
        return None

    return f'{libPaths[index]}/steamapps/common/{manifest['AppState']['installdir']}'

def build_game_manifest():
    games = []

    libs = get_libraries()[0]
    for lib in libs:
        for file in os.listdir(os.path.join(lib, 'steamapps')):
            if file.endswith('.acf'):
                with open(os.path.join(lib, 'steamapps', file)) as f:
                    data = vdf.loads(f.read())
                    games.append(data['AppState'])

    return games

def get_games_dict():
    return {f"{game['name']} ({game['appid']})": game for game in build_game_manifest()}

def get_machine_games_dict():
    return {game['name'].replace(' ', '_').lower(): game for game in build_game_manifest()}

def get_steam_config():
    with open(os.path.expanduser('~/.steam/steam/config/config.vdf'), 'r') as f:
        content = f.read()
        data = vdf.loads(content)

    return data

def get_compat_tool_mapping():
    config = get_steam_config()
    return config['InstallConfigStore']['Software']['Valve']['Steam']['CompatToolMapping']

def get_compat_tool(target_id: str):
    override = get_compat_tool_mapping().get(target_id)
    global_tool = get_compat_tool_mapping().get(0)
    if override: return override['name']
    elif global_tool: return global_tool['name']
    else: return 'proton_experimental'

def get_proton_path(name: str):
    custom_path = os.path.join(os.path.expanduser('~/.steam/steam/compatibilitytools.d/'), name)
    official = get_machine_games_dict().get(name)
    if os.path.exists(custom_path):
        return custom_path
    elif official:
        dir = get_installdir(official['appid'])
        if os.path.exists(dir): return dir
        raise NoProtonError
    else:
        raise NoProtonError

def get_last_user():
    with open(os.path.expanduser('~/.local/share/Steam/config/loginusers.vdf'), 'r') as f:
        data = vdf.loads(f.read())

    for i in data['users']:
        if data['users'][i]['MostRecent'] == '1': return i, data['users'][i]

    return 0, {
        'AccountName': 'NO LAST LOGIN',
        'PersonaName': 'NO LAST LOGIN'
    }

def get_shortcuts(user_id: str):
    account_id = int(user_id) & 0xFFFFFFFF
    with open(os.path.expanduser(f'~/.local/share/Steam/userdata/{account_id}/config/shortcuts.vdf'), 'rb') as f:
        data = vdf.binary_loads(f.read())

    return data

def build_shortcut_manifest(user_id: str):
    manifest = []
    shortcuts = get_shortcuts(user_id)
    for shortcut in shortcuts:
        obj = shortcuts[shortcut]['0']
        unsigned_id = int(obj['appid']) & 0xFFFFFFFF # we have to unsign the number for whatever reason
        manifest.append({
            'id': unsigned_id,
            'name': obj['AppName'],
            'path': obj['StartDir'],
            'prefix': os.path.expanduser(f'~/.local/share/Steam/steamapps/compatdata/{unsigned_id}/pfx/')
        })

    return manifest
