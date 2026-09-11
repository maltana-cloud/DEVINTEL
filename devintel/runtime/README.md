# DEVINTEL Runtime Integration

The runtime package is the composition root for the bounded DEVINTEL subsystems.

`DEVINTELRuntime` wires the existing core orchestrator, security orchestrator,
monitoring engine, and plugin service without moving authority into the
composition layer.

## Safety boundary

- Core permissions remain authoritative.
- Security remains authoritative for containment and recovery.
- Monitoring observes and reports; it does not authorize actions.
- Plugins are specialist capabilities, not authorities.
- High/critical actions remain owner-approval gated.
- External providers remain optional and replaceable.
- Scope IDs are retained at the runtime/reporting boundary.

The runtime is deliberately a foundation for later live adapters and owner
control surfaces; it does not invent credentials or perform external actions.
