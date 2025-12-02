import os
from prefixer.core.models import RuntimeContext
import click
from prefixer.core.registry import task_registry
from prefixer.core.tweaks import Tweak

def setup_env(ctx: RuntimeContext):
    env = os.environ.copy()
    env['WINEPREFIX'] = ctx.pfx_path
    env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(ctx.pfx_path)
    env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser('~/.steam/steam')
    return env

def run_tweak(runtime: RuntimeContext, target_tweak: Tweak):
    tasks = target_tweak.tasks

    for task in tasks:
        click.echo(f'{click.style('==>', bold=True)} {task.description} {click.style(task.type, fg='bright_black')}')
        task.resolve_paths(runtime)
        task_registry[task.type](ctx=task, runtime=runtime)
