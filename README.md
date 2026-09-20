# NetOps Config Automation

A small network configuration automation & compliance platform: a 3-router
virtual lab (FRRouting, running real OSPF), a Python automation layer built
on **Netmiko**, **Jinja2** and **YAML** that backs up, audits and pushes
config to those routers, a **FastAPI** service exposing that automation over
REST, a lightweight dashboard on top, and a **GitHub Actions** pipeline that
validates config changes before they'd ever reach a device.

## Architecture

```
 dashboard (static HTML/JS)
        |
        v  REST
   api/main.py  (FastAPI)
        |
        v
 netauto/  (render, backup, compliance, deploy)
        |
        v  SSH (Netmiko) + SFTP (Paramiko)
   r1 --- r2      3x FRRouting containers, real OSPF
    \     /       running in an isolated Docker topology
     \   /
      r3
```

- `templates/frr.conf.j2` + `host_vars/<device>.yaml` define the **intended**
  ("golden") config for each router, declaratively.
- `netauto/render.py` renders that intent into an actual FRR config — this
  part is pure and has no network dependency, so it's fully unit-testable.
- `netauto/connections.py` is the device driver: Netmiko (device_type
  `linux`, since the lab exposes a shell rather than a vendor CLI) for
  running commands, Paramiko SFTP for pushing rendered config files.
- `netauto/backup.py` / `compliance.py` / `deploy.py` are the three
  operations a real NetOps pipeline needs: snapshot the current state, diff
  it against intent, and reconcile it.
- `api/main.py` exposes all of that as REST endpoints; `dashboard/index.html`
  is a minimal UI on top.
- `.github/workflows/ci.yml` lints the YAML inventory, dry-run renders every
  device's config (catches template/host_vars errors before they'd ever
  reach a router), and runs the test suite on every push.

## Running it

Requires Docker Desktop and Python 3.10+.

```bash
python -m venv .venv
.venv/Scripts/activate      # or `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# Bring up the 3-router lab (builds the FRR+SSH image, starts containers,
# wires up the point-to-point links deterministically)
sh scripts/lab_up.sh

# Preview the golden config for a device (no network calls, pure render)
python -m netauto.cli render r1

# Push golden config to all 3 routers over SSH
python -m netauto.cli deploy all

# Check for drift against the golden config
python -m netauto.cli compliance all

# Snapshot running-config for all devices
python -m netauto.cli backup all

# Tear down
sh scripts/lab_down.sh
```

Run the API + dashboard:

```bash
uvicorn api.main:app --port 8000
python -m http.server 5500 --directory dashboard   # then open http://localhost:5500
```

Run the (offline, no Docker required) unit tests:

```bash
pytest -v
```

## Credentials

Lab SSH credentials default to `root` / `frrlab123` (see
`inventory/devices.yaml`) 

<img width="1917" height="1017" alt="image" src="https://github.com/user-attachments/assets/6e8307f4-c0ca-4b2b-9fa9-185a98674b1e" />
<img width="1450" height="725" alt="image" src="https://github.com/user-attachments/assets/7e3f0205-7df9-4ac9-b171-74f35ad3ccde" />
<img width="1917" height="1017" alt="image" src="https://github.com/user-attachments/assets/d230a722-f91d-41e7-8a96-95c56c03f876" />



