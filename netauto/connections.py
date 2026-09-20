from __future__ import annotations

import os
import pathlib

import paramiko
import yaml
from netmiko import ConnectHandler

ROOT = pathlib.Path(__file__).resolve().parent.parent
INVENTORY_PATH = ROOT / "inventory" / "devices.yaml"


def load_inventory() -> dict:
    with INVENTORY_PATH.open() as f:
        return yaml.safe_load(f)["devices"]


def get_device_params(device_name: str) -> dict:
    devices = load_inventory()
    if device_name not in devices:
        raise KeyError(f"Unknown device '{device_name}'")
    params = dict(devices[device_name])

    # Allow credentials to be overridden via environment variables instead of
    # living in inventory/devices.yaml, e.g. NETAUTO_R1_PASSWORD or the
    # blanket NETAUTO_PASSWORD. Mirrors how you'd keep secrets out of an
    # Ansible/Netmiko inventory in a real environment (vault / CI secrets).
    env_password = os.environ.get(f"NETAUTO_{device_name.upper()}_PASSWORD") or os.environ.get(
        "NETAUTO_PASSWORD"
    )
    if env_password:
        params["password"] = env_password
    return params


class FRRDevice:
    """Automation driver for the lab's FRR routers.

    Uses Netmiko (device_type="linux") for command execution over SSH, since
    the containers expose a normal shell rather than a vendor CLI, and
    Paramiko SFTP for pushing rendered configs. On real network hardware
    (Cisco IOS/NX-OS, Arista EOS, etc.) only the netmiko device_type and the
    push mechanism would change - the render/compliance/backup logic above
    this layer stays the same.
    """

    def __init__(self, device_name: str):
        self.name = device_name
        params = get_device_params(device_name)
        self._netmiko_params = {
            "device_type": "linux",
            "host": params["host"],
            "port": params.get("port", 22),
            "username": params["username"],
            "password": params["password"],
        }
        self._conn = None

    def __enter__(self) -> "FRRDevice":
        self._conn = ConnectHandler(**self._netmiko_params)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._conn:
            self._conn.disconnect()

    def get_running_config(self) -> str:
        return self._conn.send_command('vtysh -c "show running-config"')

    def get_facts(self) -> dict:
        version = self._conn.send_command('vtysh -c "show version"')
        interfaces = self._conn.send_command('vtysh -c "show interface brief"')
        neighbors = self._conn.send_command('vtysh -c "show ip ospf neighbor"')
        return {"version": version, "interfaces": interfaces, "ospf_neighbors": neighbors}

    def push_config(self, rendered_config: str) -> str:
        """Write a rendered config to the device and merge it into the running config."""
        remote_path = "/etc/frr/frr.conf.new"
        self._sftp_write(remote_path, rendered_config)
        apply_output = self._conn.send_command(f"vtysh -f {remote_path}", read_timeout=30)
        self._conn.send_command('vtysh -c "write memory"')
        return apply_output

    def _sftp_write(self, remote_path: str, content: str) -> None:
        ssh_client: paramiko.SSHClient = self._conn.remote_conn_pre
        sftp = ssh_client.open_sftp()
        try:
            with sftp.open(remote_path, "w") as f:
                f.write(content)
        finally:
            sftp.close()
