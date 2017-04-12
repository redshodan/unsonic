import subprocess
import pytest
from pyramid import testing


XMLLINT_TEST = \
"""<?xml version="1.0" encoding="UTF-8"?>
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok"
                   unsonic="0.0" version="1.14.0"/>
"""


@pytest.fixture(scope="session")
def xmllint():
    # Check for xmllint
    p = subprocess.Popen(["xmllint", "--format", "--schema",
                          "test/xsd/unsonic-subsonic-api.xsd", "-"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, err = p.communicate(XMLLINT_TEST.encode("utf-8"), timeout=15)
    if p.returncode:
        raise Exception("xmllint is required for the tests: " +
                        out.decode("utf-8"))


@pytest.fixture()
def ptesting(xmllint):
    yield testing
    testing.tearDown()
