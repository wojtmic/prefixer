import unittest
from unittest.mock import patch
from pathlib import Path

from prefixer.core.tweaks import index_tweak_folder, get_tweak_names, parse_tweak, get_tweak
from prefixer.core.models import TweakData


class test_tweaks(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

        """
        test_data directory structure
        ------------------------------
        ├── tweaks_dir_package
        │   ├── fonts
        │   │   ├── courier.json5
        │   │   ├── georgia.json5
        │   │   └── impact.json5
        │   ├── libs
        │   │   └── dotnet
        │   │       └── 35.json5
        │   └── reghacks
        │       ├── vram_1024.json5
        │       └── vram_2048.json5
        ├── tweaks_dir_system
        │   └── fonts
        │       ├── courier.json5
        │       └── georgia.json5
        ├── tweaks_dir_user
        │    └── fonts
        │        └── courier.json5
        └── tweaks_dir_empty
        """
        self.TEST_DATA = Path("tests/test_data")
        self.TWEAKS_DIR_USER = self.TEST_DATA / "tweaks_dir_user"
        self.TWEAKS_DIR_SYSTEM = self.TEST_DATA / "tweaks_dir_system"
        self.TWEAKS_DIR_PACKAGE = self.TEST_DATA / "tweaks_dir_package"
        self.TWEAKS_DIR_EMPTY = self.TEST_DATA / "tweaks_dir_empty"

        self.correct_fonts_courier_path = self.TWEAKS_DIR_USER / "fonts" / "courier.json5"
        self.incorrect_fonts_courier_path = self.TWEAKS_DIR_PACKAGE / "fonts" / "courier.json5"
        self.correct_fonts_courier_TweakData = TweakData(name='courier',
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


        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_index_tweak_folder(self):
        correct = {
            'fonts.courier': self.TWEAKS_DIR_PACKAGE / "fonts" / "courier.json5",
            'fonts.georgia': self.TWEAKS_DIR_PACKAGE / "fonts" / "georgia.json5",
            'fonts.impact': self.TWEAKS_DIR_PACKAGE / "fonts" / "impact.json5",
            'reghacks.vram_1024': self.TWEAKS_DIR_PACKAGE / "reghacks" / "vram_1024.json5",
            'reghacks.vram_2048': self.TWEAKS_DIR_PACKAGE / "reghacks" / "vram_2048.json5",
            'libs.dotnet.35': self.TWEAKS_DIR_PACKAGE / "libs" / "dotnet" / "35.json5"
        }

        self.assertDictEqual(index_tweak_folder(self.TWEAKS_DIR_PACKAGE), correct)
        self.assertDictEqual(index_tweak_folder(self.TWEAKS_DIR_EMPTY), {})

    def test_get_tweak_names(self):
        """
        Test the system and user dir tweak files are preferred over package tweaks.
        """
        correct = {
            'fonts.courier': self.TWEAKS_DIR_USER / "fonts" / "courier.json5",
            'fonts.georgia': self.TWEAKS_DIR_SYSTEM / "fonts" / "georgia.json5",
            'fonts.impact': self.TWEAKS_DIR_PACKAGE / "fonts" / "impact.json5",
            'reghacks.vram_1024': self.TWEAKS_DIR_PACKAGE / "reghacks" / "vram_1024.json5",
            'reghacks.vram_2048': self.TWEAKS_DIR_PACKAGE / "reghacks" / "vram_2048.json5",
            'libs.dotnet.35': self.TWEAKS_DIR_PACKAGE / "libs" / "dotnet" / "35.json5"
        }

        # TODO: Refactor tweaks.py to get rid of global variables instead of mocking.
        with patch('prefixer.core.tweaks.TWEAKS_DIR_USER', self.TWEAKS_DIR_USER), \
            patch('prefixer.core.tweaks.TWEAKS_DIR_SYSTEM', self.TWEAKS_DIR_SYSTEM), \
            patch('prefixer.core.tweaks.TWEAKS_DIR_PACKAGE', self.TWEAKS_DIR_PACKAGE):

            self.assertDictEqual(get_tweak_names(), correct)

    def test_parse_tweak(self):
        self.assertEqual(parse_tweak(self.correct_fonts_courier_path), self.correct_fonts_courier_TweakData)
        self.assertNotEqual(parse_tweak(self.incorrect_fonts_courier_path), self.correct_fonts_courier_TweakData)

    def test_get_tweak(self):
        with patch('prefixer.core.tweaks.TWEAKS_DIR_USER', self.TWEAKS_DIR_USER), \
            patch('prefixer.core.tweaks.TWEAKS_DIR_SYSTEM', self.TWEAKS_DIR_SYSTEM), \
            patch('prefixer.core.tweaks.TWEAKS_DIR_PACKAGE', self.TWEAKS_DIR_PACKAGE):

            self.assertEqual(get_tweak("fonts.courier"), self.correct_fonts_courier_TweakData)
