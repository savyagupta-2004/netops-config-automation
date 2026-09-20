from __future__ import annotations

from .connections import FRRDevice
from .render import render_config


def deploy_golden_config(device_name: str) -> str:
    """Render the golden config and push it to the device."""
    rendered = render_config(device_name)
    with FRRDevice(device_name) as device:
        return device.push_config(rendered)
