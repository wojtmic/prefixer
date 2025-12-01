from prefixer.core.helpers import setup_env
from prefixer.core.models import TaskContext, RuntimeContext, required_context
from prefixer.core.registry import task
from prefixer.core.settings import NO_DOWNLOAD, SILENCE_EXTERNAL
from prefixer.core.exceptions import BadFileError, BadDownloadError
import click
import subprocess
import zipfile
import shutil
import hashlib
import os.path
import requests

@task
@required_context('filename', 'url', 'checksum')
def download(ctx: TaskContext, runtime: RuntimeContext):
    if NO_DOWNLOAD:
        if os.path.exists(os.path.expanduser(f'~/Downloads/{ctx.filename}')):
            ctx.filename = os.path.expanduser(f'~/Downloads/{ctx.filename}')
        else:
            raise BadDownloadError

    else:
        try:
            with requests.get(ctx.url, stream=True) as response:
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                click.echo(f'Downloading {click.style(ctx.filename, 'bright_blue', bold=True)}')

                with click.progressbar(
                    iterable=response.iter_content(chunk_size=8192),
                    length=total_size,
                    label='Download Progress'
                ) as bar:
                    with open(os.path.join(runtime.operation_path, ctx.filename), 'wb') as f:
                        for chunk in bar:
                            f.write(chunk)

        except Exception as e:
            click.echo('ERROR: Unable to download file')
            click.echo(f'Exception triggered: {e}')

        click.echo('Verifying checksum...')
        sha256_hash = hashlib.sha256()

        try:
            with open(ctx.filename, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            calc_checksum = sha256_hash.hexdigest()

            if calc_checksum != ctx.checksum:
                click.secho(f'WARNING: Checksum mismatch!', fg='bright_red')
                click.secho(f'Expected: {ctx.checksum}', fg='red')
                click.secho(f'Got:      {calc_checksum}', fg='red')

                if not click.confirm('Do you want to keep this file?', default=False):
                    os.remove(ctx.filename)
                    raise BadDownloadError
                else:
                    click.secho('Keeping unverified file at user request.', fg='yellow')
        except FileNotFoundError:
            raise BadDownloadError

@task
@required_context('path', 'args')
def run_exe(ctx: TaskContext, runtime: RuntimeContext):
    env = setup_env(runtime)

    click.echo(f'Running {click.style(ctx.path, fg='bright_blue')} with args {click.style(ctx.args, fg='bright_blue')}')
    if not SILENCE_EXTERNAL:
        click.secho('Possible error message spam from external program!', fg='bright_black')
        subprocess.run([runtime.runnable_path, 'run', ctx.path, *ctx.args], env=env)
    else:
        subprocess.run([runtime.runnable_path, 'run', ctx.path, *ctx.args], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

@task
@required_context('values', 'path')
def regedit(ctx: TaskContext, runtime: RuntimeContext):
    env = setup_env(runtime)

    formatted_values = '\n'.join(
        [f'"{key}"="{value}"' for key, value in ctx.values.items()]
    )

    reg_content = f"""Windows Registry Editor Version 5.00

    [{ctx.path}]
    {formatted_values}"""

    reg_file_path = os.path.join(runtime.operation_path, 'edit.reg')
    with open(reg_file_path, 'w') as f:
        f.write(reg_content)

    subprocess.run([runtime.runnable_path, 'run', 'regedit', f'Z:{reg_file_path}'], env=env)

@task
@required_context('path', 'filename')
def extract(ctx: TaskContext, runtime: RuntimeContext):
    if not os.path.exists(ctx.path):
        click.echo("Target path non-existent, creating")
        os.makedirs(ctx.path)

    try:
        with zipfile.ZipFile(os.path.join(runtime.operation_path, ctx.filename), "r") as zip_ref:
            zip_ref.extractall(ctx.path)
        click.echo('Extracted!')

    except zipfile.BadZipFile:
        raise BadFileError

@task
@required_context('path', 'new_path')
def copy(ctx: TaskContext, runtime: RuntimeContext):
    click.echo(f'Copying {click.style(ctx.path, fg='bright_blue')} to {click.style(ctx.new_path, fg='bright_blue')}...')

    if os.path.isfile(ctx.path):
        shutil.copy(ctx.path, ctx.new_path)
    else:
        shutil.copytree(ctx.path, ctx.new_path, dirs_exist_ok=True)

@task
@required_context('path', 'new_path')
def rename(ctx: TaskContext, runtime: RuntimeContext):
    click.echo(f'Renaming {click.style(ctx.path, fg='bright_blue')} to {click.style(ctx.new_path, fg='bright_blue')}...')
    os.rename(ctx.path, ctx.new_path)

@task
@required_context('path')
def delete(ctx: TaskContext, runtime: RuntimeContext):
    click.echo(f'Deleting {click.style(ctx.path, fg='bright_blue')}...')

    if os.path.isfile(ctx.path):
        os.remove(ctx.path)
    else:
        shutil.rmtree(ctx.path)

@task
@required_context('path', 'content')
def create(ctx: TaskContext, runtime: RuntimeContext):
    click.echo(f'Creating {click.style(ctx.path, fg='bright_blue')}...')

    with open(ctx.path, 'w') as f:
        f.write(ctx.content)
