from pathlib import Path

from prefixer.core.helpers import setup_env, run_tweak
from prefixer.core.models import TaskContext, RuntimeContext, required_context
from prefixer.core.registry import task
from prefixer.core.settings import NO_DOWNLOAD, SILENCE_EXTERNAL, ALLOW_SHELL
from prefixer.core.exceptions import BadFileError, BadDownloadError, MalformedTaskError
from prefixer.core.tweaks import build_tweak
from prefixer.coldpfx.regedit import parser, writer
from prefixer.coldpfx.regedit.models import RegistryNode
import click
import subprocess
import zipfile
import shutil
import hashlib
import os.path
import requests
import sys

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
            headers = {
                'User-Agent': 'Prefixer/1.3.2 (Linux)'
            }

            with requests.get(ctx.url, stream=True, headers=headers, allow_redirects=True) as response:
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
            with open(os.path.join(runtime.operation_path, ctx.filename), "rb") as f:
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
    click.echo(f'Running {click.style(ctx.path, fg='bright_blue')} with args {click.style(ctx.args, fg='bright_blue')}')
    runtime.prefix.run(Path(ctx.path), ctx.args)

@task
@required_context('values', 'path', 'filename')
def regedit(ctx: TaskContext, runtime: RuntimeContext):
    target_file = ctx.filename if ctx.filename else 'user.reg'
    reg_path = os.path.join(runtime.pfx_path, target_file)

    hive = parser.parse_hive_file(reg_path)

    node_path = ctx.path.replace('\\', '\\\\')

    if node_path not in hive.nodes:
        hive.nodes[node_path] = RegistryNode(node_path, 0, {})

    node = hive.nodes[node_path]

    for key, value in ctx.values.items():
        if isinstance(value, str) and not value.startswith(('hex:', 'dword:')): node.set(key, f'"{value}"')
        else: node.set(key, value)

    shutil.copy(reg_path, os.path.join(runtime.pfx_path, f'{target_file}.bak'))
    writer.write_to_file(hive, reg_path)

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
@required_context('path', 'filename')
def extract_cab(ctx: TaskContext, runtime: RuntimeContext):
    if not os.path.exists(ctx.path):
        click.echo("Target path non-existent, creating")
        os.makedirs(ctx.path)

    click.echo(f"Extracting CAB {ctx.filename}...")

    subprocess.run(['cabextract', '-q', '-d', ctx.path, os.path.join(runtime.operation_path, ctx.filename)], check=True)

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

@task
@required_context('name')
def tweak(ctx: TaskContext, runtime: RuntimeContext):
    run_tweak(runtime, build_tweak(ctx.name))

@task
@required_context('filename', 'name')
def install_font(ctx: TaskContext, runtime: RuntimeContext):
    source_path = os.path.join(runtime.operation_path, ctx.filename)
    fonts_dir = os.path.join(runtime.pfx_path, 'drive_c', 'windows', 'Fonts')
    dest_path = os.path.join(fonts_dir, ctx.filename)

    click.echo(f'Installing font {click.style(ctx.name, fg='bright_blue')} {click.style(f'({ctx.filename})', fg='bright_black')}...')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    shutil.copy(source_path, dest_path)

    regedit_ctx = TaskContext('Apply registry edit for font', 'regedit',
                              path='Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts',
                              values={ctx.name: ctx.filename},
                              filename='system.reg')
    regedit(regedit_ctx, runtime)

@task
@required_context('content')
def message(ctx: TaskContext, runtime: RuntimeContext):
    click.echo(ctx.content)

@task
@required_context()
def pause(ctx: TaskContext, runtime: RuntimeContext):
    click.pause()

@task
@required_context('action')
def wineserver(ctx: TaskContext, runtime: RuntimeContext):
    flags = {'kill': '-k', 'wait': '-w'}

    if ctx.action not in flags:
        raise MalformedTaskError(f'Invalid wineserver action {ctx.action}')

    if ctx.action == 'wait':
        click.echo("Waiting for prefix processes to exit... (this might take a while)")
    elif ctx.action == 'kill':
        click.echo(f"Forcibly terminating prefix {click.style(runtime.pfx_path, fg='bright_blue')}...")

    runtime.prefix.run(Path('wineserver'), args=flags[ctx.action])
    click.secho('Done!', fg='bright_blue')

@task
@required_context('values', 'path', 'filename')
def edit_ini(ctx: TaskContext, runtime: RuntimeContext):
    filepath = ctx.filename
    section = ctx.path

    click.echo(f'Editing INI {click.style(filepath, fg="bright_blue")} [{section}]')

    # For any possible contributors: We aren't using configparser to avoid stripping comments or janky formats (like some Bethesda games use)
    # Any pull requests that replace this implementation with configparser will be rejected
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write(f"[{section}]\n")
            for k, v in ctx.values.items():
                f.write(f"{k}={v}\n")
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    target_header = f"[{section}]"
    section_idx = next((i for i, line in enumerate(lines) if line.strip() == target_header), -1)

    if section_idx == -1:
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(f"\n{target_header}\n")
        for k, v in ctx.values.items():
            lines.append(f"{k}={v}\n")
    else:
        keys_written = []

        for i in range(section_idx + 1, len(lines)):
            line = lines[i]
            if line.strip().startswith('['):
                break

            for k, v in ctx.values.items():
                if line.strip().lower().startswith(f"{k.lower()}="):
                    lines[i] = f"{k}={v}\n"
                    keys_written.append(k)

        for k, v in reversed(list(ctx.values.items())):
            if k not in keys_written:
                lines.insert(section_idx + 1, f"{k}={v}\n")

    with open(filepath, 'w') as f:
        f.writelines(lines)

@task
@required_context('path', 'values')
def text_replace(ctx: TaskContext, runtime: RuntimeContext):
    with open(ctx.path, 'r') as f:
        content = f.read()

    for old, new in ctx.values:
        content = content.replace(old, new)

    with open(ctx.path, 'w') as f:
        f.write(content)

@task
@required_context('path')
def register_dll(ctx: TaskContext, runtime: RuntimeContext):
    env = setup_env(runtime)

    if not os.path.exists(ctx.path):
        click.secho(f"ERROR: DLL not found at {ctx.path}", fg='red')
        return

    click.echo(f"Registering DLL: {click.style(ctx.path, fg='bright_blue')}")

    # subprocess.run([runtime.runnable_path, 'run', 'regsvr32', '/s', ctx.path], env=env)
    runtime.prefix.run(Path('regsvr32'), ['/s', ctx.path])

    click.secho('Registered!', fg='bright_blue')
