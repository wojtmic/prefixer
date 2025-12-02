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