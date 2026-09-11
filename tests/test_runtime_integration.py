from devintel.core.contracts import ActionRequest, ActionRisk
from devintel.runtime import DEVINTELRuntime


def test_runtime_wires_core_and_reports_owner_snapshot():
    runtime = DEVINTELRuntime()
    runtime.register_action("ping", lambda payload: {"ok": True, "payload": payload})

    result = runtime.execute(ActionRequest(action="ping", payload={"scope_id": "channel:a"}))

    assert result.success is True
    snapshot = runtime.snapshot("channel:a")
    assert snapshot.scope_id == "channel:a"
    assert snapshot.monitoring_state == "unknown"
    assert snapshot.metrics["requests.total"] == 1
    assert snapshot.audit_events >= 2


def test_runtime_keeps_high_risk_actions_approval_gated():
    runtime = DEVINTELRuntime()
    runtime.register_action("danger", lambda _: "should-not-run")

    denied = runtime.execute(
        ActionRequest(action="danger", risk=ActionRisk.HIGH, reason="sensitive")
    )

    assert denied.success is False
    assert "approval" in denied.message.lower()
    assert runtime.context.snapshot_metrics()["requests.succeeded"] == 0


def test_runtime_snapshot_exposes_plugin_state_without_granting_authority():
    runtime = DEVINTELRuntime()
    snapshot = runtime.snapshot("scope:test")
    assert snapshot.plugin_status == ()
    assert snapshot.scope_id == "scope:test"
