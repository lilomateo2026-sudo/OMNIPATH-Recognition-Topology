# OMNI HIVELOCITY REMOTE UPGRADE DESIGN CHANNEL

## Channel identity

This chat/thread is the human control plane for Hivelocity upgrade design.
The first implementation surface is the Hivelocity Python Orchestrator.

## Topology

```text
CHAT / HUMAN
    |
    v
ANDROID TERMUX
  omni-online
    |
    v
  omni-hv
    |
    v
OMNI HIVELOCITY FLAGSHIP
    |
    v
PYTHON ORCHESTRATOR
    |
    +--> existing adaptive model router
    +--> multiverse bridge / dual-node router
    +--> recollection + vector services
    +--> OMNI TEMPLE / Shadow-Omega
    +--> systemd runtime services
    +--> evidence + SHA lineage
```

## Authority model

- Chat: intention, architecture, approval, review.
- Android/Termux: remote console and bridge witness.
- Hivelocity: persistent flagship/state authority.
- Python Orchestrator: observe, classify, route, design, and issue receipts.
- Existing engines: perform specialized work after explicit staging/testing gates.

## Upgrade state machine

`PROPOSED -> INSPECTED -> DESIGNED -> STAGED -> TESTED -> VERIFIED -> SEALED`

A DESIGNED upgrade is not RUNNING. A STAGED upgrade is not VERIFIED.

## V1 safety contract

V1 is read-mostly. It does not restart services, replace models, mutate production
configuration, or run expensive inference. It observes state, classifies requests,
routes them to existing OMNI lanes, and produces SHA-256 receipts.

When host load pressure is >= 0.80 of logical CPU count, execution mode is forced
to `DESIGN_ONLY`. Otherwise a request may become `SANDBOX_ELIGIBLE`, but production
mutation still requires a separate test and verification gate.

## Commands

From Android Termux:

```bash
omni-online
omni-hv 'omni-upgrade status'
omni-hv 'omni-upgrade design "upgrade model routing and evidence receipts"'
```

## Evidence location

- `/opt/omni-sfc/remote-upgrade-channel/receipts/`
- `/opt/omni-sfc/remote-upgrade-channel/state/latest.json`

Every observation/design packet receives canonical JSON SHA-256 identity.
