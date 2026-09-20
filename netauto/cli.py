from __future__ import annotations

import click

from .backup import backup_device
from .compliance import check_device_compliance
from .connections import load_inventory
from .deploy import deploy_golden_config
from .render import render_config


def _device_names(device: str) -> list[str]:
    if device == "all":
        return list(load_inventory().keys())
    return [device]


@click.group()
def cli() -> None:
    """NetOps config automation CLI."""


@cli.command(name="render")
@click.argument("device")
def render_cmd(device: str) -> None:
    """Print the rendered golden config for DEVICE (or 'all')."""
    for name in _device_names(device):
        click.echo(f"===== {name} =====")
        click.echo(render_config(name))


@cli.command()
@click.argument("device")
def backup(device: str) -> None:
    """Pull and store the running-config for DEVICE (or 'all')."""
    for name in _device_names(device):
        path = backup_device(name)
        click.echo(f"[{name}] backed up running-config -> {path}")


@cli.command()
@click.argument("device")
def compliance(device: str) -> None:
    """Diff DEVICE's running-config against its golden config (or 'all')."""
    exit_code = 0
    for name in _device_names(device):
        report = check_device_compliance(name)
        status = "COMPLIANT" if report.compliant else "DRIFTED"
        click.echo(f"[{name}] {status}")
        if not report.compliant:
            exit_code = 1
            click.echo("\n".join(report.diff))
    raise SystemExit(exit_code)


@cli.command()
@click.argument("device")
def deploy(device: str) -> None:
    """Render and push the golden config to DEVICE (or 'all')."""
    for name in _device_names(device):
        output = deploy_golden_config(name)
        click.echo(f"[{name}] golden config deployed")
        if output:
            click.echo(output)


if __name__ == "__main__":
    cli()
