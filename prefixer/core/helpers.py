import os
from prefixer.core.models import RuntimeContext


def setup_env(ctx: RuntimeContext):
    env = os.environ.copy()
    env['WINEPREFIX'] = ctx.pfx_path
    env['STEAM_COMPAT_DATA_PATH'] = os.path.dirname(ctx.pfx_path)
    env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = os.path.expanduser('~/.steam/steam')
    return env
