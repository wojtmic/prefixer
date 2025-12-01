from prefixer.core.models import TweakData, TaskContext, RuntimeContext
from prefixer.core.paths import TWEAKS_DIR_USER, TWEAKS_DIR_SYSTEM
import os
import json5
from typing import List

class Tweak:
    def __init__(self, name: str, description: str, tasks: List[TaskContext]):
        self.name = name
        self.description = description
        self.tasks = tasks

TWEAKS_PATHS = [TWEAKS_DIR_SYSTEM, TWEAKS_DIR_USER]

def get_tweaks():
    tweaks = {}
    for tweakpath in TWEAKS_PATHS:
        if not os.path.exists(tweakpath):
            os.makedirs(tweakpath)

        tweakFiles = os.listdir(tweakpath)

        for tweak in tweakFiles:
            with open(os.path.join(tweakpath, tweak), 'r') as f:
                obj = json5.loads(f.read())

            tasks = obj['tasks']
            desc = obj['description']
            tweakName = tweak.split('.')[0]

            tweaks[tweakName] = TweakData(tweakName, desc, tasks)

    return tweaks

tweaks = get_tweaks()

def get_tweak(name: str):
    return tweaks[name]

def build_tweak(name: str):
    tweak = get_tweak(name)
    tasks = []
    for t in tweak.tasks:
        tasks.append(TaskContext(**t))

    return Tweak(tweak.name, tweak.description, tasks)
