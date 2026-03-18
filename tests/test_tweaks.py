from unittest.mock import patch
from pathlib import Path

from prefixer.core.tweaks import index_tweak_folder, get_tweak_names, parse_tweak, get_tweak
from prefixer.core.models import TweakData


"""
test_data directory structure
------------------------------
├── tweaks_dir_package
│   ├── fonts
│   │   ├── courier.json5
│   │   ├── georgia.json5
│   │   └── impact.json5
│   ├── libs
│   │   └── dotnet
│   │       └── 35.json5
│   └── reghacks
│       ├── vram_1024.json5
│       └── vram_2048.json5
├── tweaks_dir_system
│   └── fonts
│       ├── courier.json5
│       └── georgia.json5
├── tweaks_dir_user
│    └── fonts
│        └── courier.json5
└── tweaks_dir_empty
"""

TEST_DATA = Path("tests/test_data")
TWEAKS_DIR_USER = TEST_DATA / "tweaks_dir_user"
TWEAKS_DIR_SYSTEM = TEST_DATA / "tweaks_dir_system"
TWEAKS_DIR_PACKAGE = TEST_DATA / "tweaks_dir_package"
TWEAKS_DIR_EMPTY = TEST_DATA / "tweaks_dir_empty"

correct_fonts_courier_path = TWEAKS_DIR_USER / "fonts" / "courier.json5"
incorrect_fonts_courier_path = TWEAKS_DIR_PACKAGE / "fonts" / "courier.json5"
correct_fonts_courier_TweakData = TweakData(name='courier',
          filename=Path('tests/test_data/tweaks_dir_user/fonts/courier.json5'),
          description='Microsoft Courier New Font',
          conditions=[],
          tasks=[
            {'description': 'Download package',
             'type': 'download',
             'url': 'https://downloads.sourceforge.net/project/corefonts/the%20fonts/final/courie32.exe',
             'checksum': 'bb511d861655dde879ae552eb86b134d6fae67cb58502e6ff73ec5d9151f3384',
             'filename': 'courie32.exe'
            },
            {'description': 'Run installer',
             'type': 'run_exe',
             'path': 'courie32.exe',
             'args': ['/q', '/r:n']
            },
            {'description':
             'Wait for wineserver',
             'type': 'wineserver',
             'action': 'wait'
            }
          ])


def test_index_tweak_folder():
    correct = {
        'fonts.courier': TWEAKS_DIR_PACKAGE / "fonts" / "courier.json5",
        'fonts.georgia': TWEAKS_DIR_PACKAGE / "fonts" / "georgia.json5",
        'fonts.impact': TWEAKS_DIR_PACKAGE / "fonts" / "impact.json5",
        'reghacks.vram_1024': TWEAKS_DIR_PACKAGE / "reghacks" / "vram_1024.json5",
        'reghacks.vram_2048': TWEAKS_DIR_PACKAGE / "reghacks" / "vram_2048.json5",
        'libs.dotnet.35': TWEAKS_DIR_PACKAGE / "libs" / "dotnet" / "35.json5"
    }

    assert index_tweak_folder(TWEAKS_DIR_PACKAGE) == correct
    assert index_tweak_folder(TWEAKS_DIR_EMPTY) == {}


def test_get_tweak_names():
    """
    Test the system and user dir tweak files are preferred over package tweaks.
    """
    correct = {
        'fonts.courier': TWEAKS_DIR_USER / "fonts" / "courier.json5",
        'fonts.georgia': TWEAKS_DIR_SYSTEM / "fonts" / "georgia.json5",
        'fonts.impact': TWEAKS_DIR_PACKAGE / "fonts" / "impact.json5",
        'reghacks.vram_1024': TWEAKS_DIR_PACKAGE / "reghacks" / "vram_1024.json5",
        'reghacks.vram_2048': TWEAKS_DIR_PACKAGE / "reghacks" / "vram_2048.json5",
        'libs.dotnet.35': TWEAKS_DIR_PACKAGE / "libs" / "dotnet" / "35.json5"
    }

    # TODO: Refactor tweaks.py to get rid of global variables instead of mocking.
    with patch('prefixer.core.tweaks.TWEAKS_DIR_USER', TWEAKS_DIR_USER), \
        patch('prefixer.core.tweaks.TWEAKS_DIR_SYSTEM', TWEAKS_DIR_SYSTEM), \
        patch('prefixer.core.tweaks.TWEAKS_DIR_PACKAGE', TWEAKS_DIR_PACKAGE):

        assert get_tweak_names() == correct


def test_parse_tweak():
    assert parse_tweak(correct_fonts_courier_path) == correct_fonts_courier_TweakData
    assert parse_tweak(incorrect_fonts_courier_path) != correct_fonts_courier_TweakData


def test_get_tweak():
    with patch('prefixer.core.tweaks.TWEAKS_DIR_USER', TWEAKS_DIR_USER), \
        patch('prefixer.core.tweaks.TWEAKS_DIR_SYSTEM', TWEAKS_DIR_SYSTEM), \
        patch('prefixer.core.tweaks.TWEAKS_DIR_PACKAGE', TWEAKS_DIR_PACKAGE):

        assert get_tweak("fonts.courier") == correct_fonts_courier_TweakData
