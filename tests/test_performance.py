from click.testing import CliRunner
from prefixer.cli import prefixer
from time import time_ns


def test_version_check():
    # Why this test?
    # Need to make sure that the core isn't slowed down by specific code on basic calls
    runner = CliRunner()
    start_time = time_ns()
    result = runner.invoke(prefixer, ['--version'])

    assert result.exit_code == 0
    assert start_time - time_ns() < 1000000000
