from prefixer.core.models import TweakData, TaskContext, RuntimeContext, ConditionContext
from prefixer.core.paths import TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_PACKAGE
from prefixer.core.exceptions import NoTweakError
import os
import json5
import logging
from pathlib import Path

# TODO: These do not belong here. Set root logger in centralized location.
# TODO: Add verbose-option for command line invocation to set log-level.
logger = logging.getLogger("tweaks")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.CRITICAL) # Silence for now

class Tweak:
    def __init__(self, name: str, description: str, tasks: list[TaskContext], conditions: list[ConditionContext]):
        self.name = name
        self.description = description
        self.tasks = tasks
        self.conditions = conditions

# TWEAKS_PATHS = [TWEAKS_DIR_PACKAGE, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_USER]
TWEAKS_PATHS = [TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_PACKAGE]

def index_tweak_folder(folder: Path | str) -> dict[str, Path]:
    """
    Get all tweak files in the given directory and its subdirectories.

    returns: dict where key is the tweak name and value path-object to tweak-file.
    """
    tweaks: dict[str, Path] = {}
    folder = Path(folder)

    tweak_files = list(folder.rglob("*.json5")) + list(folder.rglob("*.json"))

    if not tweak_files:
        logger.warning(f"No tweak json files found in {folder}")
    else:
        logger.debug(f"Found {len(tweak_files)} tweaks in {folder}")

    for tweak_file in tweak_files:
        # Generate the tweak category layer from the directory structure excluding the 
        # given parent directory, e.g. /usr/share/prefixer/tweaks/fonts/font_tweak_A.json5 -> fonts.font_tweak_A
        # where /usr/share/prefixer/tweaks/ was the parent directory given as function argument.
        layer = ".".join([x for x in tweak_file.parent.parts if x not in folder.parts])
        tweak_name = tweak_file.stem
        full_tweak_name = f"{layer}.{tweak_name}"

        tweaks[full_tweak_name] = tweak_file

    return tweaks

def parse_tweak(tweak_file: Path) -> TweakData:
    """
    Read and parse the data from tweak file into TweakData-object.
    """
    with open(tweak_file, 'r') as f:
        obj: dict = json5.load(f)
    logger.debug(f"Parsed succesfully file: {tweak_file}")

    obj['conditions'] = [] if 'conditions' not in obj.keys() else obj['conditions']

    return TweakData(tweak_file.stem, tweak_file, obj['description'], obj['conditions'], obj['tasks'])

def get_tweaks() -> dict[str, TweakData]:
    """
    Read and parse all tweaks.
    """
    for tweakpath in TWEAKS_PATHS:
        if not os.path.exists(tweakpath):
            try:
                os.makedirs(tweakpath)
            except PermissionError:
                continue

    tweak_names = get_tweak_names()

    # Example code on using multiprocessing to parse the JSON-files in parallel.
    # Currently left unused due the general jankiness of python multiprocessing.
    # > with ProcessPoolExecutor(max_workers=8) as exec:
    # >     tweaks = exec.map(parse_tweak, tweak_names.values())
 
    tweaks = ( parse_tweak(tweak_file) for tweak_file in tweak_names.values() )
    return { tweak_name: tweak for tweak_name, tweak in zip(tweak_names.keys(), tweaks)}

def get_tweak(name: str) -> TweakData:
    """
    Read and parse single tweak.
    """
    tweak_names = get_tweak_names()
    if name not in tweak_names:
        raise NoTweakError(name)

    return parse_tweak(tweak_names[name])

def build_tweak(name: str):
    tweak = get_tweak(name)
    tasks = []
    for t in tweak.tasks:
        tasks.append(TaskContext(**t))

    conditions = []
    for c in tweak.conditions:
        if 'invert' not in c: c['invert'] = False
        conditions.append(ConditionContext(**c))

    return Tweak(name=tweak.name, description=tweak.description, conditions=conditions, tasks=tasks)


def get_tweak_names() -> dict[str, Path]:
    """
    Get all tweak names and the path to the tweak file.
    """
    package_tweak_files = index_tweak_folder(TWEAKS_DIR_PACKAGE)
    system_tweak_files = index_tweak_folder(TWEAKS_DIR_SYSTEM)
    user_tweak_files = index_tweak_folder(TWEAKS_DIR_USER)

    # TODO: Deduplication is a bit clumsy...
    for name in system_tweak_files:
        if name in package_tweak_files:
            logger.debug(f"Ignoring file {package_tweak_files[name]}, same tweak is found with higher priority from {TWEAKS_DIR_SYSTEM}")

    # Combining dicts with OR the priority goes from right to left.
    # Keys from the right operand will overwrite the keys of the left operand.
    all_tweak_files = package_tweak_files | system_tweak_files

    for name in user_tweak_files:
        if name in all_tweak_files:
            logger.debug(f"Ignoring file {all_tweak_files[name]}, same tweak is found with higher priority from {TWEAKS_DIR_USER}")

    all_tweak_files |= user_tweak_files

    return all_tweak_files
