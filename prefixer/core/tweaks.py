from prefixer.core.models import TweakData, TaskContext, RuntimeContext, ConditionContext
from prefixer.core.paths import TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_PACKAGE
from prefixer.core.exceptions import NoTweakError
import os
import json5
from typing import List

class Tweak:
    def __init__(self, name: str, description: str, tasks: List[TaskContext], conditions: List[ConditionContext]):
        self.name = name
        self.description = description
        self.tasks = tasks
        self.conditions = conditions

# TWEAKS_PATHS = [TWEAKS_DIR_PACKAGE, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_USER]
TWEAKS_PATHS = [TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM, TWEAKS_DIR_PACKAGE]

def index_tweak_folder(folder: str, layer: str = ''):
    tweak_files = os.listdir(folder)
    tweaks = {}

    for tweak in tweak_files:
        path = os.path.join(folder, tweak)
        if os.path.isdir(path):
            tweaks |= index_tweak_folder(path, f'{layer}{tweak}.')
            continue

        if not (tweak.endswith('.json5') or tweak.endswith('.json')): continue

        tweak_name = tweak.split('.')[0]
        if f'{layer}{tweak_name}' in tweaks.keys(): continue

        with open(path, 'r') as f:
            obj: dict = json5.loads(f.read())

        tasks = obj['tasks']
        desc = obj['description']

        if 'conditions' in obj: conditions = obj['conditions']
        else: conditions = []

        tweaks[f'{layer}{tweak_name}'] = TweakData(tweak_name, desc, conditions, tasks)

    return tweaks

def get_tweaks():
    all_tweaks = {}
    for tweakpath in TWEAKS_PATHS:
        if not os.path.exists(tweakpath):
            try: os.makedirs(tweakpath)
            except PermissionError: continue

        tweaks = index_tweak_folder(tweakpath)
        all_tweaks |= tweaks

    return all_tweaks

def get_tweak(name: str):
    tweaks = get_tweaks()
    if not name in tweaks: raise NoTweakError(name)
    return tweaks[name]

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


def scan_tweak_names(folder: str, layer: str = ''):
    names = set()
    if not os.path.exists(folder):
        return names

    try:
        entries = os.listdir(folder)
    except PermissionError:
        return names

    for entry in entries:
        path = os.path.join(folder, entry)
        if os.path.isdir(path):
            names.update(scan_tweak_names(path, f"{layer}{entry}."))
        elif entry.endswith(('.json', '.json5')):
            tweak_name = entry.split('.')[0]
            names.add(f"{layer}{tweak_name}")

    return names


def get_tweak_names():
    all_names = set()
    for tweakpath in TWEAKS_PATHS:
        all_names.update(scan_tweak_names(tweakpath))
    return all_names
