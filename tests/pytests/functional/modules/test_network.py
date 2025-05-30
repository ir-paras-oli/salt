"""
Validate network module
"""

import pytest

import salt.utils.platform

pytestmark = [
    pytest.mark.windows_whitelisted,
    pytest.mark.requires_network,
]


@pytest.fixture(scope="module")
def url(modules):
    return "ns.google.com"


@pytest.fixture(scope="module")
def network(modules):
    return modules.network


@pytest.mark.slow_test
def test_network_ping(network, url):
    """
    network.ping
    """
    ret = network.ping(url)

    # Github Runners are on Azure, which doesn't allow ping
    packet_loss = "100% packet loss"
    if salt.utils.platform.is_windows():
        packet_loss = "100% loss"

    if packet_loss not in ret.lower():
        exp_out = ["ping", url, "ms", "time"]
        for out in exp_out:
            assert out in ret.lower()
    else:
        assert packet_loss in ret.lower()


@pytest.mark.skip_on_darwin(reason="Not supported on macOS")
@pytest.mark.slow_test
def test_network_netstat(network):
    """
    network.netstat
    """
    ret = network.netstat()
    exp_out = ["proto", "local-address"]
    for val in ret:
        for out in exp_out:
            assert out in val


@pytest.mark.skip_if_binaries_missing("traceroute")
@pytest.mark.slow_test
def test_network_traceroute(network, url):
    """
    network.traceroute
    """
    ret = network.traceroute(url)
    exp_out = ["hostname", "ip"]
    for val in ret:
        if not val:
            continue
        for out in exp_out:
            if val["hostname"] == "*" and out == "ip":
                # These entries don't have an ip key
                continue
            assert out in val


@pytest.mark.slow_test
@pytest.mark.skip_unless_on_windows
def test_network_nslookup(network, url):
    """
    network.nslookup
    """
    ret = network.nslookup(url)
    exp_out = {"Server", "Address"}
    for val in ret:
        if not exp_out:
            break
        for out in list(exp_out):
            if out in val:
                exp_out.remove(out)
    if exp_out:
        pytest.fail(f"Failed to find the {exp_out} key(s) on the returned data: {ret}")
