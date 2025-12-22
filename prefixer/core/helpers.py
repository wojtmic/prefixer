import os
from prefixer.core.models import RuntimeContext, TaskContext
import click
from prefixer.core.registry import task_registry
from prefixer.core.tweaks import Tweak

def setup_env(ctx: RuntimeContext):
    env = os.environ.copy()
    env['WINEPREFIX'] = ctx.pfx_path
    env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(ctx.pfx_path)
    env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser('~/.steam/steam')
    return env

def add_tweak_to_file(file: str, tweak: str):
    with open(file, 'a') as f:
        f.write(tweak)
        f.write('\n')

def run_tweak(runtime: RuntimeContext, target_tweak: Tweak):
    tasks = target_tweak.tasks

    for task in tasks:
        click.echo(f'{click.style('==>', bold=True)} {task.description} {click.style(task.type, fg='bright_black')}')
        task.resolve_paths(runtime)
        task_registry[task.type](ctx=task, runtime=runtime)

    # task_registry['wineserver'](runtime=runtime, ctx=TaskContext(description='wait for wine to finish', type='wineserver', action='wait'))

    ran_tweak_file = os.path.join(runtime.pfx_path, 'tweaks.prefixer.txt')

    if not os.path.exists(ran_tweak_file):
        add_tweak_to_file(ran_tweak_file, target_tweak.name)
        return

    with open(ran_tweak_file, 'r') as f:
        content = f.read()
        if target_tweak.name in content: return

    add_tweak_to_file(ran_tweak_file, target_tweak.name)