# DEVINTEL Plugin / Specialist Engine Layer

Plugins are replaceable specialist capabilities attached to the stable DEVINTEL core. Examples planned later include video generation, crypto intelligence, memecoin analysis, football intelligence, image generation, and audio/voice.

## Boundary
`CORE -> PluginService -> PluginRuntime -> approved plugin handler`

A plugin is not authority. Registration does not grant publishing, payment, deployment, account, or security privileges. High/critical actions require explicit owner approval. Failed execution isolates the affected plugin instead of bringing down unrelated plugins.

## Lifecycle
`DISCOVERED -> ENABLED -> DISABLED / ISOLATED / FAILED`

Re-registering a plugin at a new version increments its generation. The registry is bounded and thread-safe.

## Design rules
- Provider-independent; no vendor is mandatory.
- Scope IDs travel with actions; plugins do not choose broader authority from scope.
- Secrets must remain outside plugin source/artifacts.
- Plugin failures are contained to the plugin.
- The security/permission systems remain authoritative.
- Plugin code must be tested and executed through an appropriate sandbox before production deployment; this foundation does not execute arbitrary source.
- Future engines plug in without modifying the intelligence core contracts.
