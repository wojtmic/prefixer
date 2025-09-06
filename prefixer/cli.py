import os
import subprocess
import click
import core.steam as steam
import core.tweaks as tweaks
import sys
from pathlib import Path
import tempfile

@click.group()
@click.argument('game_id')
@click.pass_context
def prefixer(ctx, game_id: str):
    """
    Modern tool to manage Proton prefixes.
    """
    ctx.obj = {'GAME_ID': game_id}

    game_id_styled = click.style(game_id, fg='bright_blue')

    click.echo(f'Targeting => {game_id_styled}')
    pfx_path = steam.get_prefix_path(game_id)
    if pfx_path is None:
        games = steam.build_game_manifest()
        index = next((i for i, item in enumerate(games) if item['name'] == game_id), None)
        if not index is None:
            # This means the game WAS found by name!
            ctx.obj['GAME_ID'] = games[index]['appid'] # Correct the game ID to the actual number
            game_id = ctx.obj['GAME_ID']
            pfx_path = steam.get_prefix_path(game_id)  # Find the PFX path again
        else:
            click.echo('ERROR: Unable to find the wineprefix')
            sys.exit(1)


    ctx.obj['PFX_PATH'] = pfx_path
    ctx.obj['PFX_CONFIG_INFO'] = f'{pfx_path}/../config_info'

    # Find binary path
    with open(ctx.obj['PFX_CONFIG_INFO'], 'r') as f:
        configInfo = f.readlines()

    binaryPath= Path(f'{configInfo[2]}/../../bin/wine').resolve()
    ctx.obj['BINARY_PATH'] = binaryPath

    click.echo(f'Prefix Path => {click.style(pfx_path, fg='bright_blue')}')
    click.echo(f'Binary Location => {click.style(binaryPath, fg='bright_blue')}')

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

    env['WINEPREFIX'] = pfx_path
    subprocess.run([bin_path, 'winecfg'], env=env)

@prefixer.command()
@click.argument('exe_path')
@click.pass_context
def run(ctx, exe_path: str):
    """
    Runs a .exe within the target prefix
    """
    if not os.path.exists(exe_path):
        click.echo('The file could not be found')
        sys.exit(1)

    pfx_path = ctx.obj['PFX_PATH']
    bin_path = ctx.obj['BINARY_PATH']

    env = os.environ.copy()
    env['WINEPREFIX'] = pfx_path

    click.echo(f'Running {exe_path}...')
    subprocess.run([bin_path, exe_path], env=env)

@prefixer.command()
@click.argument('tweak_name')
@click.pass_context
def tweak(ctx, tweak_name: str):
    """
    Apply a tweak
    """
    # First, we obtain the essential information: binary & prefix paths
    pfxPath = ctx.obj['PFX_PATH']
    binaryPath = ctx.obj['BINARY_PATH']

    # Load the tweak
    allTweaks = tweaks.get_tweaks()

    if not tweak_name in allTweaks:
        click.echo('ERROR: Unable to find the requested tweak')
        sys.exit(1)

    targetTweak = allTweaks[tweak_name]
    tasks = targetTweak['tasks']

    if len(tasks) <= 0:
        click.echo('ERROR: This tweak contains no tasks to run')
        sys.exit(1)

    # Execute the tasks
    click.echo(f'Target Tweak => {click.style(targetTweak['description'])}')

    with tempfile.TemporaryDirectory(prefix='prefixer-') as tempPath:
        for task in tasks:
            tweaks.run_task(task, pfxPath, binaryPath, tempPath)

    click.secho('All tasks completed successfully!', fg='bright_green')

if __name__ == '__main__':
    prefixer()
