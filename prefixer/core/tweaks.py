from urllib.parse import urlparse
import json5
import subprocess
import os
import requests
import hashlib
import click
import sys

TWEAKS_DIR = os.path.expanduser('~/.config/prefixer/tweaks')

def get_tweaks():
    tweakFiles = os.listdir(TWEAKS_DIR)
    tweaks = {}

    for tweak in tweakFiles:
        with open(os.path.join(TWEAKS_DIR, tweak), 'r') as f:
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
    filename: str = os.path.basename(urlparse(url).path)

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
    click.secho('Possible error message spam from external program!', color='bright_black')
    subprocess.run([binary, filePath, *task['args']], env=env)

def run_task(task, pfx, binary, opPath):
    desc = task['description']
    type = task['type']

    click.echo(f'{click.style('==>', bold=True)} {desc} {click.style(f'({type})', fg='bright_black')}')

    if type == 'download':
        filename = task_download(task, opPath)
        if filename is None:
            click.secho('Error while downloading file, aborting.', fg='red')
            sys.exit(1)

    elif type == 'runexe':
        task_runexe(task, pfx, binary, opPath)

    else:
        click.echo(f'Unrecognized task {click.style(type, bold=True)}. Check if the task name is written correctly or update Prefixer.')
        sys.exit(1)

    click.secho(f'Completed task {desc} successfully!', fg='bright_blue')
