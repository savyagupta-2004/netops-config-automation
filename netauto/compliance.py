from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from .connections import FRRDevice
from .render import render_config

_IGNORED_PREFIXES = ("Building configuration", "!", "Current configuration", "%")
# FRR always echoes these structural closers and a git-suffixed version
# string in `show running-config`; they carry no configuration intent, so
# treating them as drift would just be diff noise on every single device.
_IGNORED_LINES = {"exit", "end"}


def _normalize(config_text: str) -> list[str]:
    """Strip blank lines, comments, vtysh warnings and FRR's structural
    boilerplate so diffs only surface real config drift."""
    lines = []
    for raw in config_text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in _IGNORED_PREFIXES):
            continue
        if line.strip() in _IGNORED_LINES:
            continue
        if line.startswith("frr version"):
            continue
        lines.append(line)
    return lines


@dataclass
class ComplianceReport:
    device: str
    compliant: bool
    diff: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"device": self.device, "compliant": self.compliant, "diff": self.diff}


def compare_configs(device_name: str, golden_config: str, live_config: str) -> ComplianceReport:
    golden_lines = _normalize(golden_config)
    live_lines = _normalize(live_config)

    diff = list(
        difflib.unified_diff(
            live_lines,
            golden_lines,
            fromfile="live-running-config",
            tofile="golden-config",
            lineterm="",
        )
    )
    return ComplianceReport(device=device_name, compliant=len(diff) == 0, diff=diff)


def check_device_compliance(device_name: str) -> ComplianceReport:
    """Render the golden config from the template + host_vars and diff it
    against what's actually running on the device right now."""
    golden = render_config(device_name)
    with FRRDevice(device_name) as device:
        live = device.get_running_config()
    return compare_configs(device_name, golden, live)
