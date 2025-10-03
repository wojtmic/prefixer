import vdf
import os
import sys
from .exceptions import NoSteamError

LIBMANIFEST_LOCATION = os.path.expanduser('~/.steam/steam/steamapps/libraryfolders.vdf')

def get_libraries():
    if not os.path.exists(LIBMANIFEST_LOCATION):
        # print('ERROR: You do not have a Steam library manifest file in your home directory and Prefixer is unable to continue. Please add a Steam library or install Steam.')
        raise NoSteamError

    with open(LIBMANIFEST_LOCATION, 'r') as f:
        libmanifest = vdf.loads(f.read())

    # Get lib IDs
    libs = []
    for lib in libmanifest['libraryfolders']:
        if not os.path.exists(libmanifest['libraryfolders'][lib]['path']): continue
        libs.append(lib)

    # Get paths to libs
    libPaths = []
    for lib in libs:
        libPaths.append(libmanifest['libraryfolders'][lib]['path'])

    # Get apps/IDs of games in said libs
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
                    games.append(vdf.loads(f.read())['AppState'])

    return games

def get_games_dict():
    return {f"{game['name']} ({game['appid']})": game for game in build_game_manifest()}
