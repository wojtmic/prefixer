import os
import shutil
import subprocess
import click
from prefixer.core import steam
from prefixer.core import tweaks
from prefixer.core import exceptions as excs
import tempfile
import sys
from prefixer.core.models import RuntimeContext
from prefixer.core.registry import task_registry
from prefixer.core.tweaks import Tweak
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

        game_id_styled = click.style(game_id, fg='bright_blue')

        click.echo(f'Targeting => {game_id_styled}')
        pfx_path = steam.get_prefix_path(game_id)
        if pfx_path is None:
            index = next((i for i, item in enumerate(games) if item['name'] == game_id), None)
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

@prefixer.command()
@click.argument('exe_path')
@click.pass_context
def run(ctx, exe_path: str):
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
    subprocess.run([bin_path, 'run', exe_path], env=env)

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

def run_tweak(runtime: RuntimeContext, target_tweak: Tweak):
    tasks = target_tweak.tasks

    for task in tasks:
        click.echo(f'{click.style('==>', bold=True)} {task.description} {click.style(task.type, fg='bright_black')}')
        task.resolve_paths(runtime)
        task_registry[task.type](ctx=task, runtime=runtime)

@prefixer.command()
@click.argument('tweak_name')
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
        runtime = RuntimeContext(game_id, pfx_path, tempdir, game_path, runnable_path)
        run_tweak(runtime, target_tweak)

    click.secho('All tasks completed successfully!', fg='bright_green')

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

    except excs.InternalExeError:
        click.secho('ERROR: There was an error while running an external exe within the tweak!', fg='bright_red')

    # except Exception as e:
    #     click.secho(f'ERROR: An unknown exception has occurred: {e}', fg='bright_red')
