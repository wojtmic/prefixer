from prefixer.core.models import TweakData, TaskContext, RuntimeContext, ConditionContext
from prefixer.core.paths import TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM
import os
import json5
from typing import List

class Tweak:
    def __init__(self, name: str, description: str, tasks: List[TaskContext], conditions: List[ConditionContext]):
        self.name = name
        self.description = description
        self.tasks = tasks
        self.conditions = conditions

TWEAKS_PATHS = [TWEAKS_DIR_SYSTEM, TWEAKS_DIR_USER]

def index_tweak_folder(folder: str, layer: str = ''):
    tweak_files = os.listdir(folder)
    tweaks = {}

    for tweak in tweak_files:
        path = os.path.join(folder, tweak)
        if os.path.isdir(path):
            tweaks |= index_tweak_folder(path, f'{layer}{tweak}.')
            continue

        if not (tweak.endswith('.json5') or tweak.endswith('.json')): continue

        with open(path, 'r') as f:
            obj: dict = json5.loads(f.read())

        tasks = obj['tasks']
        desc = obj['description']
        tweak_name = tweak.split('.')[0]

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

tweaks = get_tweaks()

def get_tweak(name: str):
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
