# pynaads

Python library to monitor Pelmorex's NAADS service and parse Common Alerting Protocol (CAP) alerts.

## Overview

`pynaads` is aimed at public weather and emergency alert feeds from Pelmorex's NAADS service. In practice, that means CAP-based alerts such as severe thunderstorm, tornado, flood, evacuation, public safety, and other emergency/warning conditions that are delivered as structured XML. The parser is generic enough for CAP-style alert payloads, and the included samples are weather-focused examples from the Pelmorex feed.

Pelmorex NAADS data is not limited to one message type: the feed can carry event metadata, geographic polygons or circles, geocodes, urgency/severity/certainty, references, TTS audio, embedded media, and other alert attachments. This library exposes that data in Python objects so it can be filtered, inspected, and routed downstream.

Typical CAP payloads in the Pelmorex ecosystem include severe weather events (tornado, thunderstorm, flood, wind, winter storm), public safety warnings, and emergency notifications that produce location-aware alerts. The parser is designed for that broader CAP model, so it can handle alerts beyond the weather-only examples included in the test suite.

## Installation

Install from PyPI:

```bash
pip install pynaads
```

Install from a local checkout:

```bash
cd pynaads
python -m pip install -e .
```

## Quick start

```python
import pynaads

client = pynaads.naads(passhb=True)

xml = """
<alert>
  <identifier>example-alert</identifier>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <sender>testSender@Pelmorex-test</sender>
  <sent>2018-04-13T09:35:16-04:00</sent>
  <status>Actual</status>
  <info>
    <category>Geo</category>
    <event>Severe Thunderstorm</event>
  </info>
</alert>
"""

parsed = client.parse(xml)
print(parsed.event["identifier"])
print(parsed.event["msgType"])
```

## Connecting to the live stream

```python
import pynaads
import time

client = pynaads.naads(passhb=False)
client.connect()
client.start()

while True:
    item = client.getQueue()
    if item is not False:
        for alert in item:
            print(alert)
    time.sleep(0.5)
```

The `connect()` method opens the TCP socket to the NAADS stream; `start()` launches a background thread that reads and parses incoming alert messages. The queue can be checked with `getQueue()` to retrieve events as they arrive.

## Filtering alerts

The library includes helpers for checking if an alert intersects a point or if an event matches a specific CLC code:

```python
client = pynaads.naads(passhb=True)
alert = client.parse(xml)

# Use a single point or a list of points
inside = client.filter_in_geo(alert, (45.42, -75.69))

# Filter on land-cover code values
is_local = client.filter_in_clc(alert, ["044110", "044120"])
```

`filter_in_geo()` accepts tuple or list-based coordinate inputs and checks the alert polygon or multipolygon coverage. `filter_in_clc()` helps match event geocode values, such as Canadian land-cover codes.

## Library structure

- `pynaads.naads` provides the stream client and parsing helpers.
- `pynaads.event` contains the event and area models used to map CAP XML into Python objects.
- `test/samples/` contains the sample CAP XML files used for regression coverage.

## Running tests

From the project root:

```bash
python -m pip install -e .
python -m pytest
```

The project includes sample XML files under `test/samples/` and tests each one to ensure it parses successfully.
