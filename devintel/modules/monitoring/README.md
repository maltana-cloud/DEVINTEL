# System #10 — Monitoring & Owner Control

System #10 provides operational visibility without becoming an authority layer.

## Responsibilities
- component and channel health
- queue/backlog snapshots
- operational errors and alerts
- owner-visible reports
- counters for security and revenue visibility
- scope-isolated monitoring state

## Boundary
Monitoring observes and reports. It does not grant permissions, spend money, publish content, join communities, deploy tools, or change security state by itself. Existing System #3 permission/security boundaries remain authoritative.

Security events can be surfaced to the authorized owner while internal defensive mechanisms remain quiet to external users.

The store is bounded and thread-safe. Every record is associated with a scope so one channel, domain, plugin, or other component cannot contaminate another scope's report.

Plugin health can use this module as its operational reporting destination; plugin authority remains controlled by the plugin/runtime and core permission layers.
