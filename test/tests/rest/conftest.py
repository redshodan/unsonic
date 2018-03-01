import subprocess


XMLLINT_TEST = \
    """<?xml version="1.0" encoding="UTF-8"?>
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok"
                   unsonic="0.0" version="1.14.0"/>
""".encode("utf-8")


def pytest_configure(config):
    # Check for docker
    p = subprocess.Popen(["docker", "info"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    out, err = p.communicate(None, timeout=15)
    if p.returncode:
        raise Exception("docker is required for the tests: ")

    # Check for xmllint
    p = subprocess.Popen(["xmllint", "--format", "--schema",
                          "test/xsd/unsonic-subsonic-api.xsd", "-"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    out, err = p.communicate(XMLLINT_TEST, timeout=15)
    if p.returncode:
        raise Exception("xmllint is required for the tests: ")
