from prefixer.coldpfx.regedit import parser, writer
from prefixer.coldpfx.regedit.models import RegistryNode

hive = """WINE REGISTRY Version 2
;; All keys relative to REGISTRY\\Machine

#arch=win64

[Software\\Prefixer\\Tests] 1757166416
@="TEST"
"testint"="1"
"teststr"="Test"
"testdword"=dword:00000000
"testhex"=hex:00,00,00,00,00,00,00,00"""

def test_parse():
    parsed_hive = parser.parse_hive(hive.split('\n'))

    assert parsed_hive.arch == 'win64'
    assert parsed_hive.header == 'WINE REGISTRY Version 2'
    assert parsed_hive.nodes['Software\\Prefixer\\Tests'] == RegistryNode(
        'Software\\Prefixer\\Tests',
        timestamp=1757166416,
        changed=False,
        values={
            '@': '"TEST"',
            'testint': '"1"',
            'teststr': '"Test"',
            'testdword': 'dword:00000000',
            'testhex': 'hex:00,00,00,00,00,00,00,00'
        }
    )

def test_modify():
    parsed_hive = parser.parse_hive(hive.split('\n'))
    parsed_hive.nodes['Software\\Prefixer\\Tests'].set('testint', '"2"')

    assert parsed_hive.nodes['Software\\Prefixer\\Tests'].changed
    assert parsed_hive.nodes['Software\\Prefixer\\Tests'].get('testint') == '"2"'

def test_serialize():
    hive_raw = hive.split('\n')
    parsed_hive = parser.parse_hive(hive_raw)
    lines = writer.serialize(parsed_hive)

    assert lines[0] == hive_raw[0]
    assert lines[1] == hive_raw[1]
    assert lines[3] == hive_raw[3]
    assert lines[5] == hive_raw[5]

    assert sorted(lines[6:]) == sorted(hive_raw[6:])
