from pathlib import Path

import pytest

import pynaads

SAMPLE_DIR = Path(__file__).parent / "samples"
SAMPLE_FILES = sorted(SAMPLE_DIR.glob("*"))


@pytest.mark.parametrize("sample_file", SAMPLE_FILES, ids=lambda path: path.name)
def test_each_sample_file_parses(sample_file):
    xml = sample_file.read_text(encoding="utf-8")

    parsed = pynaads.naads(passhb=True).parse(xml)

    assert parsed is not False
    assert hasattr(parsed, "event")
    assert isinstance(parsed.event, dict)
    assert isinstance(parsed.event.get("identifier"), str)
    assert parsed.event["identifier"]
    assert isinstance(parsed.event.get("msgType"), str)
    assert parsed.event["msgType"]
    assert isinstance(parsed.event.get("sender"), str)
    assert parsed.event["sender"]
    assert "info" in parsed.event
