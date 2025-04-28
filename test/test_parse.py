import pytest
import pynaads

def test_placeholder(sample01):
    naads = pynaads.naads(passhb=True)
    parsed = naads.parse(sample01)
    assert parsed.event['identifier'] == '78A038D9-701C-659D-47A8-7C54C13884C2'
    assert parsed.event['msgType'] == 'Alert'
    assert parsed.event['scope'] == 'Public'
    assert parsed.event['sender'] == 'testSender@Pelmorex-test'
    assert parsed.event['sent'] == '2018-04-13T09:35:16-04:00'
    assert parsed.event['status'] == 'Actual'
    assert parsed.event['info'] == []
