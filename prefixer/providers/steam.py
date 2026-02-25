from prefixer.providers.classes import Prefix, PrefixProvider
from prefixer.core.exceptions import NoSteamError, NoProtonError, ProviderError
from pathlib import Path
from subprocess import run, DEVNULL
from os import environ
import vdf

STEAMPATH = Path('~/.steam/steam').expanduser()
LIBMANIFEST_LOCATION = STEAMPATH / 'steamapps' / 'libraryfolders.vdf'

class SteamPrefix(Prefix):
    def __init__(self, pfx_path: Path, files_path: Path, binary_path: Path, proton_script_path: Path, name: str):
        super().__init__(pfx_path, files_path, binary_path, name)

        self.proton_script_path = proton_script_path

    def run(self, exe: Path, args: list[str] = None, silent: bool = False):
        env = environ.copy()

        env['WINEPREFIX'] = str(self.pfx_path)
        env['STEAM_COMPAT_DATA_PATH'] = str(self.pfx_path.parent)
        env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = str(STEAMPATH)

        if not silent:
            run([str(self.proton_script_path), 'run', str(exe), *(args or [])], env=env)
        else:
            run([str(self.proton_script_path), 'run', str(exe), *(args or [])], env=env, stdout=DEVNULL, stderr=DEVNULL)

class SteamPrefixProvider(PrefixProvider):
    def get_libraries(self):
        if not LIBMANIFEST_LOCATION:
            raise NoSteamError

        with open(LIBMANIFEST_LOCATION, 'r') as f:
            libmanifest = vdf.load(f)

        libs = []
        for lib in libmanifest['libraryfolders']:
            if not Path(libmanifest['libraryfolders'][lib]['path']).exists(): continue
            libs.append(lib)

        lib_paths = []
        for lib in libs:
            lib_paths.append(libmanifest['libraryfolders'][lib]['path'])

        lib_apps = []
        for lib in libs:
            lib_apps.append(libmanifest['libraryfolders'][lib]['apps'])

        return lib_paths, lib_apps

    def get_prefix_path(self, target_id: str) -> Path:
        libs = self.get_libraries()
        lib_paths = libs[0]
        apps = libs[1]

        index = next((i for i, app in enumerate(apps) if target_id in app), None)
        if index is None:
            return None

        return Path(f'{lib_paths[index]}/steamapps/compatdata/{target_id}/pfx')

    def get_manifest(self, target_id: str) -> Path:
        libs = self.get_libraries()
        lib_paths = libs[0]
        apps = libs[1]

        index = next((i for i, app in enumerate(apps) if target_id in app), None)
        if index is None:
            return None

        path = Path(f'{lib_paths[index]}/steamapps/appmanifest_{target_id}.acf')
        with open(str(path), 'r') as f:
            manifest_data = vdf.loads(f.read())

        return manifest_data

    def get_installdir(self, target_id: str):
        manifest = self.get_manifest(target_id)
        libs = self.get_libraries()
        lib_paths = libs[0]
        apps = libs[1]

        index = next((i for i, app in enumerate(apps) if target_id in app), None)
        if index is None:
            return None

        return Path(f'{lib_paths[index]}/steamapps/common/{manifest['AppState']['installdir']}')

    def build_game_manifest(self):
        games = []

        libs = self.get_libraries()[0]
        for lib in libs:
            for file in (Path(lib) / 'steamapps').glob('*.acf'):
                with open(str(file), 'r') as f:
                    data = vdf.loads(f.read())
                    games.append(data['AppState'])

        return games

    def get_games_dict(self):
        return {f"{game['name']} ({game['appid']})": game for game in self.build_game_manifest()}

    def get_game_id_dict(self):
        return {game['name']: game['appid'] for game in self.build_game_manifest()}

    def get_machine_games_dict(self):
        return {game['name'].replace(' ', '_').lower(): game for game in self.build_game_manifest()}

    def get_steam_config(self):
        with open(str(STEAMPATH / 'config' / 'config.vdf'), 'r') as f:
            content = f.read()
            data = vdf.loads(content)

        return data

    def get_compat_tool_mapping(self):
        config = self.get_steam_config()
        return config['InstallConfigStore']['Software']['Valve']['Steam']['CompatToolMapping']

    def get_compat_tool(self, target_id: str):
        override = self.get_compat_tool_mapping().get(target_id)
        global_tool = self.get_compat_tool_mapping().get(0)
        if override:
            return override['name']
        elif global_tool:
            return global_tool['name']
        else:
            return 'proton_experimental'

    def get_proton_path(self, name: str):
        custom_path = STEAMPATH / 'compatibilitytools.d' / name
        custom_sys_path = Path('/usr/share/steam/compatibilitytools.d') / name

        official = self.get_machine_games_dict().get(name)
        if custom_path.exists(): return custom_path
        elif custom_sys_path.exists(): return custom_sys_path
        elif official:
            dir = self.get_installdir(official['appid'])
            if dir.exists(): return dir
            raise NoProtonError
        else: raise NoProtonError

    def get_last_user(self):
        with open(str(STEAMPATH / 'config' / 'loginusers.vdf'), 'r') as f:
            data = vdf.loads(f.read())

        for i in data['users']:
            if data['users'][i]['MostRecent'] == '1': return i, data['users'][i]

        return 0, {
            'AccountName': 'NO LAST LOGIN',
            'PersonaName': 'NO LAST LOGIN'
        }

    def get_shortcuts(self, user_id: str):
        account_id = int(user_id) & 0xFFFFFFFF
        with open((STEAMPATH/'userdata' / str(account_id) / 'config' / 'shortcuts.vdf'), 'rb') as f:
            data = vdf.binary_loads(f.read())

        return data

    def build_shortcut_manifest(self, user_id: str):
        manifest = []
        shortcuts = self.get_shortcuts(user_id)
        for shortcut in shortcuts:
            obj = shortcuts[shortcut]['0']
            unsigned_id = int(obj['appid']) & 0xFFFFFFFF  # we have to unsign the number for whatever reason
            manifest.append({
                'id': unsigned_id,
                'name': obj['AppName'],
                'path': obj['StartDir'],
                'prefix': STEAMPATH / 'steamapps' / 'compatdata' / str(unsigned_id) / 'pfx'
            })

        return manifest

    def get_prefixes(self) -> dict[str, str]:
        prefixes = self.get_game_id_dict()

        user_id, _ = self.get_last_user()
        if user_id == 0: raise ProviderError('Could not detect user ID from Steam files. Have you logged into Steam?')
        shortcuts = self.build_shortcut_manifest(user_id)
        parsed = {s['name']: str(s['id']) for s in shortcuts}

        prefixes |= parsed

        return dict(sorted(prefixes.items()))

    def get_prefix_by_index(self, index: int) -> SteamPrefix:
        """Returns a Prefix by index."""
        prefixes = self.get_prefixes()
        id = list(prefixes.values())[index]
        return self.get_prefix(id)

    def get_prefix(self, id: str) -> SteamPrefix:
        name = next((k for k, v in self.get_prefixes().items() if v == id), None)

        pfx_path = self.get_prefix_path(id)
        if pfx_path:
            files_path = self.get_installdir(id)
            tool_name = self.get_compat_tool(id)
            proton_root = self.get_proton_path(tool_name)

            return SteamPrefix(
                pfx_path=pfx_path,
                files_path=files_path,
                binary_path=proton_root,
                proton_script_path=proton_root / 'proton',
                name=name
            )

        user_id, _ = self.get_last_user()
        if user_id != 0:
            try:
                shortcuts = self.build_shortcut_manifest(user_id)
                match = next((s for s in shortcuts if str(s['id']) == id), None)
                if match:
                    tool_name = self.get_compat_tool(id)
                    proton_root = self.get_proton_path(tool_name)

                    return SteamPrefix(
                        pfx_path=Path(match['prefix']),
                        files_path=Path(match['path']),
                        binary_path=proton_root,
                        proton_script_path=proton_root / 'proton',
                        name=name
                    )
            except (FileNotFoundError, KeyError):
                pass

        return None
