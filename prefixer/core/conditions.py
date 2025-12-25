from prefixer.core.models import ConditionContext, RuntimeContext, required_context
from prefixer.core.registry import condition
import os

@condition
@required_context('value')
def file_exists(ctx: ConditionContext, runtime: RuntimeContext):
    return os.path.exists(ctx.value)

@condition
@required_context('value', 'matches')
def file_matches(ctx: ConditionContext, runtime: RuntimeContext):
    return os.path.samefile(ctx.value, ctx.matches)

@condition
@required_context('value', 'matches')
def env_matches(ctx: ConditionContext, runtime: RuntimeContext):
    return os.environ[ctx.value] == ctx.matches
