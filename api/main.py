from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from netauto.backup import backup_device
from netauto.compliance import check_device_compliance
from netauto.connections import load_inventory
from netauto.deploy import deploy_golden_config
from netauto.render import render_config

app = FastAPI(title="NetOps Config Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_device(name: str) -> None:
    if name not in load_inventory():
        raise HTTPException(status_code=404, detail=f"Unknown device '{name}'")


@app.get("/devices")
def list_devices():
    inventory = load_inventory()
    return [
        {"name": name, "host": params["host"], "role": params.get("role", "router")}
        for name, params in inventory.items()
    ]


@app.get("/devices/{name}/golden-config")
def get_golden_config(name: str):
    _validate_device(name)
    return {"device": name, "config": render_config(name)}


@app.post("/devices/{name}/backup")
def trigger_backup(name: str):
    _validate_device(name)
    path = backup_device(name)
    return {"device": name, "backup_path": str(path)}


@app.get("/devices/{name}/compliance")
def get_compliance(name: str):
    _validate_device(name)
    report = check_device_compliance(name)
    return report.to_dict()


@app.post("/devices/{name}/deploy")
def trigger_deploy(name: str):
    _validate_device(name)
    output = deploy_golden_config(name)
    return {"device": name, "result": output}
