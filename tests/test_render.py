from netauto.render import render_config


def test_render_r1_contains_hostname_and_router_id():
    config = render_config("r1")
    assert "hostname r1" in config
    assert "ospf router-id 10.0.0.1" in config


def test_render_r1_contains_all_interfaces():
    config = render_config("r1")
    assert "interface eth1" in config
    assert "ip address 10.12.0.2/29" in config
    assert "interface eth2" in config
    assert "ip address 10.13.0.2/29" in config
    assert "interface lo" in config
    assert "ip address 10.0.0.1/32" in config


def test_render_r1_contains_ospf_networks():
    config = render_config("r1")
    assert "network 10.0.0.1/32 area 0.0.0.0" in config
    assert "network 10.12.0.0/29 area 0.0.0.0" in config
    assert "network 10.13.0.0/29 area 0.0.0.0" in config


def test_render_is_deterministic():
    assert render_config("r2") == render_config("r2")


def test_unknown_device_raises():
    import pytest

    with pytest.raises(FileNotFoundError):
        render_config("does-not-exist")
