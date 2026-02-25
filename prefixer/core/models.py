from dataclasses import dataclass
from functools import wraps
from typing import Optional, List, Dict
from prefixer.core.exceptions import MalformedTaskError
from inspect import signature
from prefixer.providers.classes import Prefix

@dataclass
class RuntimeContext:
    """Dynamic runtime values for tasks"""
    prefix: Prefix
    """The Prefix"""
    operation_path: str
    """Temporary directory for performing operations"""

    @property
    def pfx_path(self): return str(self.prefix.pfx_path)

    @property
    def game_path(self): return str(self.prefix.files_path)

@dataclass
class ConditionContext:
    """Condition that needs to pass before running tweak/task"""
    type: str
    """Type of this condition; view core.conditions"""
    invert: bool
    """Inverts the condition"""
    value: str = None
    """Value name; depends on condition type"""
    matches: str = None
    """Secondary value; depends on condition type"""
    path: str = None
    """Path; depends on condition type"""
    filename: str = None
    """Filename; depends on condition type"""
    values: Dict[str, str] = None
    """List of values; depends on condition type"""

    def resolve_paths(self, runtime: RuntimeContext) -> None:
        replacers = {
            '<gamedir>': runtime.game_path,
            '<pfxdir>': runtime.pfx_path,
            '<tempdir>': runtime.operation_path,
        }

        def _apply_replacements(text: Optional[str]) -> Optional[str]:
            if not text:
                return text

            for placeholder, value in replacers.items():
                if value:
                    text = text.replace(placeholder, value)
            return text

        self.value = _apply_replacements(self.value)
        self.matches = _apply_replacements(self.matches)

@dataclass
class TaskContext:
    """General config context for Prefixer tweak tasks"""
    description: str
    """Description of this task"""
    type: str
    """Type of this task; view core.tasks"""
    conditions: Optional[List[ConditionContext]] = None
    """Conditions to run this task"""
    filename: Optional[str] = None
    """File name; depends on task type"""
    checksum: Optional[str] = None
    """SHA256 Checksum; depends on task type"""
    url: Optional[str] = None
    """URL; depends on task type"""
    path: Optional[str] = None
    """Generic path; depends on task type"""
    new_path: Optional[str] = None
    """Generic new path; depends on task type"""
    name: Optional[str] = None
    """Generic name; depends on task type"""
    method: Optional[str] = None
    """Method of operation; depends on task type"""
    args: Optional[List[str]] = None
    """Arguments; depends on task type"""
    values: Optional[Dict[str, str]] = None
    """Key-value values; depends on task type"""
    content: Optional[str] = None
    """Contents; depends on task type"""
    action: Optional[str] = None
    """Task-specific action; depends on task type"""

    def resolve_paths(self, runtime: RuntimeContext) -> None:
        replacers = {
            '<gamedir>': runtime.game_path,
            '<pfxdir>': runtime.pfx_path,
            '<tempdir>': runtime.operation_path,
        }

        def _apply_replacements(text: Optional[str]) -> Optional[str]:
            if not text:
                return text

            for placeholder, value in replacers.items():
                if value:
                    text = text.replace(placeholder, value)
            return text

        self.filename = _apply_replacements(self.filename)
        self.path = _apply_replacements(self.path)
        self.new_path = _apply_replacements(self.new_path)

        if self.args: self.args = [_apply_replacements(arg) for arg in self.args]

@dataclass
class TaskData:
    """Task-representative data"""
    description: str
    config: TaskContext

@dataclass
class TweakData:
    """Prefixer tweak in raw, unparsed form"""
    name: str
    description: str
    conditions: Optional[List[ConditionContext]]
    tasks: List[Dict[str, str]]

def required_context(*keys: str):
    """Checks if the passed context contains required keys"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature(func).bind(*args, **kwargs)
            bound.apply_defaults()
            ctx = bound.arguments['ctx']

            missing = [k for k in keys if not getattr(ctx, k, None)]
            extra   = [k for k, v in vars(ctx).items() if v and k not in keys and k not in {'type', 'description', 'invert', 'conditions'}]

            if len(missing) > 0: raise MalformedTaskError(f'Too little fields! Should contain {keys}')
            if len(extra) > 0:   raise MalformedTaskError(f'Too many fields! Should contain {keys}')

            return func(*args, **kwargs)
        return wrapper
    return decorator
