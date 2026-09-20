from __future__ import annotations

import datetime as dt
import pathlib

from .connections import FRRDevice

ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / "backups"


def backup_device(device_name: str) -> pathlib.Path:
    """Pull the live running-config and store a timestamped snapshot + a
    'latest.conf' pointer, similar to a config-backup step in a network
    change pipeline."""
    with FRRDevice(device_name) as device:
        running_config = device.get_running_config()

    device_dir = BACKUP_DIR / device_name
    device_dir.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = device_dir / f"{timestamp}.conf"
    snapshot_path.write_text(running_config)

    latest_path = device_dir / "latest.conf"
    latest_path.write_text(running_config)

    return snapshot_path
