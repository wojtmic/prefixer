import os
from importlib import resources

TWEAKS_DIR_USER = os.path.expanduser('~/.config/prefixer/tweaks')
TWEAKS_DIR_SYSTEM = os.path.expanduser('/usr/share/prefixer/tweaks')
TWEAKS_DIR_PACKAGE = str(resources.files('prefixer').joinpath('data/tweaks'))
