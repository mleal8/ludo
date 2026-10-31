"""The per-system emulator RPC accepts only compatible standalone choices."""

from ludo_app.backend import LudoBackend


class _SettingsSpy:
    def __init__(self):
        self.values = {}

    def set_platform_emulator_override(self, slug, emulator):
        self.values[slug] = emulator


def _run(coroutine):
    """These backend RPCs have no suspension points, so run them without IOCP."""
    try:
        coroutine.send(None)
    except StopIteration as finished:
        return finished.value
    raise AssertionError('RPC unexpectedly suspended')


def test_set_platform_emulator_override_accepts_compatible_choice():
    backend = LudoBackend.__new__(LudoBackend)
    backend._retroarch = _SettingsSpy()

    result = _run(backend.set_platform_emulator_override('ps2', 'pcsx2'))

    assert result['success'] is True
    assert backend._retroarch.values == {'ps2': 'pcsx2'}


def test_set_platform_emulator_override_rejects_wrong_system():
    backend = LudoBackend.__new__(LudoBackend)
    backend._retroarch = _SettingsSpy()

    result = _run(backend.set_platform_emulator_override('wiiu', 'dolphin'))

    assert result['success'] is False
    assert result['message'] == 'Emulator does not support this system'
    assert backend._retroarch.values == {}


def test_set_platform_emulator_override_can_return_to_auto():
    backend = LudoBackend.__new__(LudoBackend)
    backend._retroarch = _SettingsSpy()

    result = _run(backend.set_platform_emulator_override('psx', ''))

    assert result['success'] is True
    assert backend._retroarch.values == {'psx': ''}
