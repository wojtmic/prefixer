import os
import shutil
import subprocess
import click
from click.shell_completion import shell_complete

from prefixer.core import steam
from prefixer.core import tweaks
from prefixer.core import exceptions as excs
import tempfile
import sys
from prefixer.core.models import RuntimeContext
from prefixer.core.helpers import run_tweak
from prefixer.core.tweaks import get_tweaks
import prefixer.core.tasks # Import necessary to actually load tasks!

@click.group()
@click.argument('game_id')
@click.pass_context
def prefixer(ctx, game_id: str):
    """
    Modern tool to manage Proton prefixes.
    """
    if os.geteuid() == 0:
        if os.environ.get('ALLOW_ROOT', 'false').lower() != 'true':
            click.secho('SECURITY WARNING: Prefixer CANNOT be run as root due to security, safety and integrity purposes.', fg='bright_red')
            click.secho('Running as root will make created/downloaded files read-only to your user, as well as might delete files you don\'t want to.', fg='bright_red')
            click.secho('If you are absolutely SURE that you want to run Prefixer as root, set the environment variable ALLOW_ROOT to true.', fg='bright_red')
            click.secho('The developer of Prefixer is not responsible for any damages to your device when running as root.', fg='bright_red')
            sys.exit(1)
        else:
            click.secho('WARNING: Running as root with ALLOW_ROOT override set. The developer of Prefixer is not responsible for any damages.', fg='bright_yellow')

    if os.environ.get('NO_STEAM', 'false').lower() != 'true':
        games = steam.build_game_manifest()

        ctx.obj = {'GAME_ID': game_id}

        pfx_path = steam.get_prefix_path(game_id)
        if pfx_path is None:
            index = next((i for i, item in enumerate(games) if item['name'].lower() == game_id.lower()), None)
            if not index is None:
                ctx.obj['GAME_ID'] = games[index]['appid']
                game_id = ctx.obj['GAME_ID']
                pfx_path = steam.get_prefix_path(game_id)
            else:
                raise excs.NoPrefixError


        proton_ver = steam.get_compat_tool(game_id)
        if 'steamlinuxruntime' in proton_ver:
            click.secho('This app runs natively under the Steam Linux Runtime!', fg='bright_red')
            return

        proton_path = steam.get_proton_path(proton_ver)

        ctx.obj['PROTON_VER'] = proton_ver
        ctx.obj['PFX_PATH'] = pfx_path

        game_path = steam.get_installdir(game_id)
        ctx.obj['GAME_PATH'] = game_path

        ctx.obj['BINARY_PATH'] = os.path.join(proton_path, 'proton')

    else:
        click.secho('WARNING: NO_STEAM specified. Defaulting to global wine installation.', fg='bright_yellow')

        ctx.obj['PFX_PATH'] = os.path.expanduser('~/.wine')
        ctx.obj['GAME_PATH'] = os.getcwd()
        ctx.obj['BINARY_PATH'] = shutil.which('wine')

    pfxOverride = os.environ.get('PREFIX_PATH', '')
    gamePathOverride = os.environ.get('PROGRAM_PATH', '')
    binaryOverride = os.environ.get('WINE_BINARY', '')

    if pfxOverride != '':
        ctx.obj['PFX_PATH'] = pfxOverride
    if gamePathOverride != '':
        ctx.obj['GAME_PATH'] = gamePathOverride
    if binaryOverride != '':
        ctx.obj['BINARY_PATH'] = binaryOverride

    game_id_styled = click.style(ctx.obj['GAME_ID'], fg='bright_blue')

    click.echo(f'Targeting => {game_id_styled}')
    click.echo(f'Prefix Path => {click.style(ctx.obj['PFX_PATH'], fg='bright_blue')}')
    click.echo(f'Game Path => {click.style(ctx.obj['GAME_PATH'], fg='bright_blue')}')
    click.echo(f'Binary Location => {click.style(ctx.obj['BINARY_PATH'], fg='bright_blue')}')

@prefixer.command()
@click.pass_context
def winecfg(ctx):
    """
    Opens a winecfg window for the prefix
    """
    pfx_path = ctx.obj['PFX_PATH']
    bin_path = ctx.obj['BINARY_PATH']
    click.echo('Opening winecfg...')

    env = os.environ.copy()
    env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(pfx_path)
    env['WINEPREFIX'] = pfx_path
    env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser('~/.steam/steam')

    subprocess.run([bin_path, 'run', 'winecfg'], env=env)

@prefixer.command(context_settings={"ignore_unknown_options": True})
@click.argument('exe_path')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, exe_path: str, args):
    """
    Runs a .exe within the target prefix
    """

    pfx_path = ctx.obj['PFX_PATH']
    bin_path = ctx.obj['BINARY_PATH']

    env = os.environ.copy()
    env['WINEPREFIX'] = pfx_path
    env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(pfx_path)
    env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser('~/.steam/steam')

    click.echo(f'Running {exe_path}...')
    subprocess.run([bin_path, 'run', exe_path, *args], env=env)

@prefixer.command()
@click.pass_context
def openpfx(ctx):
    """
    Opens the wineprefix folder in your file manager
    """
    subprocess.run(['xdg-open', ctx.obj['PFX_PATH']])

@prefixer.command()
@click.pass_context
def opengamedir(ctx):
    """
    Opens the gamedir folder in your file manager
    """
    subprocess.run(['xdg-open', ctx.obj['GAME_PATH']])


def complete_tweaks(ctx, param, incomplete):
    try:
        available_tweaks = get_tweaks().keys()
    except Exception:
        return []

    suggestions = [k for k in available_tweaks if k.startswith(incomplete)]

    return suggestions

@prefixer.command()
@click.argument('tweak_name', shell_complete=complete_tweaks)
@click.pass_context
def tweak(ctx, tweak_name: str):
    """
    Apply a tweak
    """
    pfx_path = ctx.obj['PFX_PATH']
    runnable_path = ctx.obj['BINARY_PATH']
    game_path = ctx.obj['GAME_PATH']
    game_id = ctx.obj['GAME_ID']

    target_tweak = tweaks.build_tweak(tweak_name)

    click.echo(f'Target Tweak => {click.style(target_tweak.description)}')

    with tempfile.TemporaryDirectory(prefix='prefixer-') as tempdir:
        runtime = RuntimeContext(game_id, pfx_path, tempdir, game_path, runnable_path, os.path.dirname(pfx_path))
        run_tweak(runtime, target_tweak)

    click.secho('All tasks completed successfully!', fg='bright_green')

@prefixer.command()
@click.pass_context
def wipe(ctx):
    """
    Completely wipes a prefix
    """
    click.secho('WARNING!', fg='bright_red')
    click.secho('This action is IRREVERSIBLE and will remove ALL files in the prefix!', fg='bright_red')
    click.secho('This may include: configuration, save files and tweaks', fg='bright_red')

    if not click.confirm('Are you sure you want to wipe the prefix?'): return

    shutil.rmtree(ctx.obj['PFX_PATH'])

@prefixer.command()
@click.pass_context
def debuginfo(ctx):
    """
    Dump debug information about the selected prefix
    """
    # Info for possible contributors: this part of the code is very messy. If someone would like to clean it up, I would be glad to accept a pull request.
    pfx_path = ctx.obj['PFX_PATH']
    ran_tweak_file = os.path.join(pfx_path, 'tweaks.prefixer.txt')

    if os.path.exists(ran_tweak_file):
        with open(ran_tweak_file, 'r') as f:
            ran_tweaks = f.readlines()
    else:
        ran_tweaks = []

    reg_section = "[Software\\\\Wine\\\\DllOverrides]"

    reg_path = os.path.join(pfx_path, 'user.reg')
    registry_data = {}

    if os.path.exists(reg_path):
        with open(reg_path, 'r', encoding='utf-8', errors='replace') as f:
            in_section = False
            for line in f:
                line = line.strip()

                if not line or line.startswith(';') or line.startswith('#'):
                    continue

                if line.startswith('['):
                    if line.startswith(reg_section):
                        in_section = True
                        continue
                    elif in_section: break
                    continue

                if in_section and '=' in line:
                    key_raw, val_raw = line.split('=', 1)

                    key = key_raw.strip('"')
                    val = val_raw
                    if val_raw.startswith('"') and val_raw.endswith('"'):
                        val = val_raw[1:-1]
                    elif val_raw.lower().startswith('dword:'):
                        val = val_raw.split(':', 1)[1]

                    registry_data[key] = val

    system32 = os.path.join(pfx_path, 'drive_c', 'windows', 'system32')

    checks = {
        "64bit": os.path.exists(os.path.join(pfx_path, 'drive_c', 'windows', 'syswow64'))
    }

    click.echo('[ PREFIXER DEBUG REPORT ]')
    click.echo(f'{click.style('TARGET', fg='bright_blue')} : {ctx.obj['GAME_ID']}')
    click.echo(f'{click.style('PROTON VERSION', fg='bright_blue')} : {ctx.obj['PROTON_VER']}')
    click.echo(f'{click.style('64-BIT', fg='bright_blue')} : {checks["64bit"]}')
    click.echo()

    click.echo('DLL Overrides')
    click.echo("="*20)
    if not registry_data:
        click.echo("(None)")
    else:
        width = max(len(k) for k in registry_data)

        for dll, mode in registry_data.items():
            click.echo(f"{dll:<{width}} : {mode}")

    click.echo()

    click.echo('Tweak History')
    click.echo('='*20)
    if not ran_tweaks:
        click.echo('(None)')
        return

    for tweak in ran_tweaks:
        click.echo(tweak)

if __name__ == '__main__':
    try:
        prefixer()

    except excs.NoTweakError:
        click.secho('ERROR: The specified tweak wasn\'t found!', fg='bright_red')
    except excs.NoSteamError:
        click.secho('ERROR: Prefixer was unable to find Steam!', fg='bright_red')
    except excs.NoTaskError:
        click.secho('ERROR: The task specified in the tweak wasn\'t found!', fg='bright_red')
    except excs.NoPrefixError:
        click.secho('ERROR: The specified Prefix couldn\'t be found!', fg='bright_red')

    except excs.BadFileError:
        click.secho('ERROR: Prefixer encountered an error with a file while executing the tweak!', fg='bright_red')
    except excs.BadDownloadError:
        click.secho('ERROR: Prefixer wasn\'t able to download a file!', fg='bright_red')
    except excs.BadTweakError:
        click.secho('ERROR: The tweak is malformed or requires a newer version of Prefixer!', fg='bright_red')
    except excs.MalformedTaskError as e:
        click.secho(f'Malformed tweak! {e}', fg='bright_red')

    except excs.InternalExeError:
        click.secho('ERROR: There was an error while running an external exe within the tweak!', fg='bright_red')
