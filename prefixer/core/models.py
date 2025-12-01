from dataclasses import dataclass
from functools import wraps
from typing import Optional, List, Dict
from prefixer.core.exceptions import MalformedTaskError
from inspect import signature

@dataclass
class RuntimeContext:
    """Dynamic runtime values for tasks"""
    game_id: str
    """SteamID of the game/app being targeted"""
    pfx_path: str
    """Wineprefix path"""
    operation_path: str
    """Temporary directory for performing operations"""
    game_path: str
    """Game path"""
    runnable_path: str
    """Path to the runnable/wrapper script for running the binary"""

@dataclass
class TaskContext:
    """General config context for Prefixer tweak tasks"""
    description: str
    """Description of this task"""
    type: str
    """Type of this task"""
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
            extra   = [k for k, v in vars(ctx).items() if v and k not in keys and k not in {'type', 'description'}]

            if len(missing) > 0: raise MalformedTaskError(f'Too little fields! Should contain {keys}')
            if len(extra) > 0:   raise MalformedTaskError(F'Too many fields! Should contain {keys}')

            return func(*args, **kwargs)
        return wrapper
    return decorator