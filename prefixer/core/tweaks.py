import zipfile
import json5
import subprocess
import os
import requests
import hashlib
import click
import sys
import shutil
from . import exceptions as excs

TWEAKS_DIR_USER = os.path.expanduser('~/.config/prefixer/tweaks')
TWEAKS_DIR_SYSTEM = os.path.expanduser('/usr/share/prefixer/tweaks')

TWEAKS_PATHS = [TWEAKS_DIR_SYSTEM, TWEAKS_DIR_USER]

def get_tweaks():
    tweaks = {}
    for tweakpath in TWEAKS_PATHS:
        if not os.path.exists(tweakpath):
            os.makedirs(tweakpath)

        tweakFiles = os.listdir(tweakpath)

        for tweak in tweakFiles:
            with open(os.path.join(tweakpath, tweak), 'r') as f:
                obj = json5.loads(f.read())

            tasks = obj['tasks']
            desc = obj['description']
            tweakName = tweak.split('.')[0]

            tweaks[tweakName] = {
                "description": desc,
                "tasks": tasks
            }

    return tweaks

def task_download(task, opPath):
    url: str = task['url']
    checksum: str = task['checksum']
    filename: str = task['filename']

    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            click.echo(f'Downloading {click.style(filename, 'bright_blue', bold=True)}')

            with click.progressbar(
                iterable=response.iter_content(chunk_size=8192),
                length=total_size,
                label='Download Progress'
            ) as bar:
                with open(os.path.join(opPath, filename), 'wb') as f:
                    for chunk in bar:
                        f.write(chunk)
    except Exception as e:
        click.echo('ERROR: Unable to download file')
        click.echo(f'Exception triggered: {e}')

    click.echo(f'Finished download, verifying checksum...')
    downloadedChecksum = hashlib.sha256()

    with open(os.path.join(opPath, filename), "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            downloadedChecksum.update(block)

    if downloadedChecksum.hexdigest() != checksum:
        click.secho('WARNING: SHA256 Checksum of the downloaded file is incorrect.', fg='red')
        if not click.confirm('Do you want to keep this file either way?', default=False):
            os.remove(os.path.join(opPath, filename))
            return None
        else:
            click.secho('Continuing with unverified file. The user takes all responsibility for possible damage done to device.', fg='yellow')
    else:
        click.secho('Checksum verified!', fg='bright_green')

    return filename

def task_runexe(task, pfx, binary, opPath):
    env = os.environ.copy()
    env['WINEPREFIX'] = pfx

    filePath = os.path.join(opPath, task['filename'])

    click.echo(f'Running {click.style(task['filename'],fg='bright_blue')} with args {click.style(task['args'], fg='bright_blue')}')
    click.secho('Possible error message spam from external program!', fg='bright_black')
    subprocess.run([binary, filePath, *task['args']], env=env)

def task_regedit(task, pfx, binary, opPath):
    path = task['path']
    values = task['contents']

    # Construct the string
    formatted_values = '\n'.join(
        [f'"{key}"="{value}"' for key, value in values.items()]
    )

    reg_content = f"""Windows Registry Editor Version 5.00
    
[{path}]
{formatted_values}"""

    # Prepare temporary file
    with open(os.path.join(opPath, 'edit.reg'), 'w') as f:
        f.write(reg_content)

    env = os.environ.copy()
    env['WINEPREFIX'] = pfx

    # Edit the registry
    subprocess.run([binary, 'regedit', f'Z:{os.path.join(opPath, 'edit.reg')}'], env=env)

def task_extract(task, pfx, gamePath, opPath):
    filename = task['filename']
    filePath: str = os.path.join(opPath, filename)

    path: str = task['path']
    path = path.replace('<gamedir>', gamePath)
    path = path.replace("<pfxdir>", pfx)
    path = path.replace("<tempdir>", opPath)

    if not os.path.exists(path):
        click.echo("Target path non-existent, creating")
        os.makedirs(path)

    try:
        with zipfile.ZipFile(filePath, "r") as zip_ref:
            zip_ref.extractall(path)
        click.echo('Extracted!')

    except zipfile.BadZipFile:
        raise excs.BadFileError

def task_fileop(task, pfx, gamePath, opPath):
    op = task['operation']

    filePath: str = task['path']
    filePath = filePath.replace('<gamedir>', gamePath)
    filePath = filePath.replace("<pfxdir>", pfx)
    filePath = filePath.replace("<tempdir>", opPath)

    if op == 'copy':
        newPath: str = task['newPath']
        newPath = newPath.replace('<gamedir>', gamePath)
        newPath = newPath.replace("<pfxdir>", pfx)
        newPath = newPath.replace("<tempdir>", opPath)

        click.echo(f'Copying {click.style(filePath, fg='bright_blue')} to {click.style(newPath, fg='bright_blue')}...')

        if os.path.isfile(filePath):
            shutil.copy(filePath, newPath)
        else:
            shutil.copytree(filePath, newPath, dirs_exist_ok=True)

    elif op == 'rename':
        newPath: str = task['newPath']
        newPath = newPath.replace('<gamedir>', gamePath)
        newPath = newPath.replace("<pfxdir>", pfx)
        newPath = newPath.replace("<tempdir>", opPath)

        click.echo(f'Renaming {click.style(filePath, fg='bright_blue')} to {click.style(newPath, fg='bright_blue')}...')
        os.rename(filePath, newPath)

    elif op == 'delete':
        click.echo(f'Deleting {click.style(filePath, fg='bright_blue')}...')

        if os.path.isfile(filePath):
            os.remove(filePath)
        else:
            shutil.rmtree(filePath)

    elif op == 'create':
        click.echo(f'Creating {click.style(filePath, fg='bright_blue')}...')

        with open(filePath, 'w') as f:
            f.write(task['contents'])

    else:
        click.secho('INCORRECT TASK OPERATION', fg='bright red')

def run_task(task, pfx, gamePath, binary, opPath, tweakList):
    desc = task['description']
    type = task['type']

    click.echo(f'{click.style('==>', bold=True)} {desc} {click.style(f'({type})', fg='bright_black')}')

    if type == 'download':
        filename = task_download(task, opPath)
        if filename is None:
            click.secho('Error while downloading file, aborting.', fg='red')
            raise excs.BadDownloadError

    elif type == 'runexe':
        task_runexe(task, pfx, binary, opPath)

    elif type == 'regedit':
        task_regedit(task, pfx, binary, opPath)

    elif type == 'extract':
        task_extract(task, pfx, gamePath, opPath)

    elif type == 'fileop':
        task_fileop(task, pfx, gamePath, opPath)

    elif type == 'tweak':
        name = task['name']

        # Throw if tweak not found
        if not name in tweakList:
            # click.echo('ERROR: Unable to find the requested tweak')
            raise excs.NoTweakError

        # Get tweak data
        targetTweak = tweakList[name]
        tasks = targetTweak['tasks']

        # and run it
        for t in tasks:
            run_task(t, pfx, gamePath, binary, opPath, tweakList)

    else:
        # click.echo(f'Unrecognized task {click.style(type, bold=True)}. Check if the task name is written correctly or update Prefixer.')
        raise excs.NoTaskError

    click.secho(f'Completed task {desc} successfully!', fg='bright_blue')
