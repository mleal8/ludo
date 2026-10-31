"""System-wide standalone emulator choices preserve existing auto routing."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from romm_sync_engine.sync_core import (  # noqa: E402
    RetroArchInterface, STANDALONE_EMULATORS,
    standalone_emulator_for_platform, standalone_emulators_for_platform,
)


class Settings:
    def __init__(self, overrides=None, paths=None):
        self.overrides = overrides or {}
        self.paths = paths or {}

    def get(self, section, key, default=''):
        if section == 'EmulatorOverrides':
            return self.overrides.get(key, default)
        if section == 'Emulators':
            return self.paths.get(key, default)
        return default


def main():
    assert standalone_emulator_for_platform('PlayStation 2', 'ps2') is None
    assert standalone_emulator_for_platform('Nintendo GameCube', 'gamecube') is None
    assert standalone_emulator_for_platform('PlayStation', 'psx') is None
    assert [key for key, _ in standalone_emulators_for_platform('PlayStation 2', 'ps2')] == ['pcsx2']
    assert [key for key, _ in standalone_emulators_for_platform('Wii', 'wii')] == ['dolphin']
    assert [key for key, _ in standalone_emulators_for_platform('Wii U', 'wiiu')] == ['cemu']
    assert [key for key, _ in standalone_emulators_for_platform('PlayStation', 'psx')] == ['duckstation']

    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / 'PCSX2.AppImage'
        exe.write_bytes(b'')
        exe.chmod(0o755)
        ra = RetroArchInterface.__new__(RetroArchInterface)
        ra.settings = Settings({'ps2': 'pcsx2'}, {'pcsx2_path': str(exe)})
        ra.retroarch_executable = None
        command, error = ra.build_launch_command(
            '/games/PS2/Game.iso', 'PlayStation 2', platform_slug='ps2')
        assert error is None
        assert command == [str(exe), '-fullscreen', '/games/PS2/Game.iso']

        # The original Switch mapping remains the automatic standalone default.
        ra.settings = Settings()
        chosen = ra.selected_standalone_emulator_status('Nintendo Switch', 'switch')
        assert chosen['key'] == 'eden'

        # The other systems stay on RetroArch unless the user explicitly opts in.
        assert ra.selected_standalone_emulator_status('PlayStation 2', 'ps2') == {}

        for key, rom, expected in (
            ('dolphin', '/games/Wii/Game.iso', [str(exe), '-b', '-e', '/games/Wii/Game.iso']),
            ('duckstation', '/games/PSX/Game.chd', [str(exe), '-fullscreen', '/games/PSX/Game.chd']),
        ):
            spec = STANDALONE_EMULATORS[key]
            assert ra.build_standalone_launch_command(rom, key, spec, str(exe)) == expected

    print('all standalone emulator choice checks passed')


if __name__ == '__main__':
    main()
