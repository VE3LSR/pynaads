from pathlib import Path
import pytest

def getfile(file):
    with open(file, "r") as f:
        return f.read()

@pytest.fixture
def sample01():
    return getfile(Path(__file__).parent / "samples/Sample1_CAPCP_No_Attachment.xml")
