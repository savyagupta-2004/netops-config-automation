from __future__ import annotations

import pathlib

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
HOST_VARS_DIR = ROOT / "host_vars"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def load_host_vars(device_name: str) -> dict:
    path = HOST_VARS_DIR / f"{device_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No host_vars file for device '{device_name}': {path}")
    with path.open() as f:
        return yaml.safe_load(f)


def render_config(device_name: str, template_name: str = "frr.conf.j2") -> str:
    """Render the golden config for a device from its Jinja2 template + host vars."""
    template = _env.get_template(template_name)
    host_vars = load_host_vars(device_name)
    return template.render(**host_vars)
