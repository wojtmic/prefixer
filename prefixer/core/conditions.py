from prefixer.coldpfx.regedit.models import RegistryNode, RegistryHive
from prefixer.core.models import ConditionContext, RuntimeContext, required_context
from prefixer.core.registry import condition
from prefixer.coldpfx.regedit import parser
import os

@condition
@required_context('filename')
def file_exists(ctx: ConditionContext, runtime: RuntimeContext):
    return os.path.exists(ctx.value)

@condition
@required_context('filename', 'matches')
def file_matches(ctx: ConditionContext, runtime: RuntimeContext):
    return os.path.samefile(ctx.value, ctx.matches)

@condition
@required_context('value', 'matches')
def env_matches(ctx: ConditionContext, runtime: RuntimeContext):
    return os.environ[ctx.value] == ctx.matches

@condition
@required_context('path', 'filename', 'values')
def reg_matches(ctx: ConditionContext, runtime: RuntimeContext):
    hive: RegistryHive = parser.parse_hive_file(os.path.join(runtime.pfx_path, ctx.filename))
    node: RegistryNode = hive.nodes.get(ctx.path.replace('\\', '\\\\'), RegistryNode(ctx.path, 0, {}, False))

    for k, v in ctx.values.items():
        if v == '!prefixer_none!': v = None
        if not node.values.get(k, None) == v: return False

    return True
