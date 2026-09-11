from devintel.control import ControlDecision, OwnerControlCenter
from devintel.runtime import DEVINTELRuntime

def test_control_snapshot_is_observation_only():
    center = OwnerControlCenter(DEVINTELRuntime())
    snap = center.snapshot("channel:test")
    assert snap.scope_id == "channel:test"
    assert snap.plugin_count == 0
    assert snap.pending_approvals == 0

def test_sensitive_command_is_approval_gated_and_consumed_after_approval():
    center = OwnerControlCenter(DEVINTELRuntime())
    command = center.request("channel:test", "sensitive", reason="owner action")
    assert center.decide(command) is ControlDecision.APPROVAL_REQUIRED
    assert center.decide(command, owner_approved=True) is ControlDecision.ALLOW
    assert center.consume(command, owner_approved=True) is ControlDecision.ALLOW
    assert center.decide(command, owner_approved=True) is ControlDecision.DENY

def test_unknown_command_fails_closed():
    center = OwnerControlCenter(DEVINTELRuntime())
    command = center.request("scope:a", "x")
    foreign = type(command)("foreign", command.scope_id, command.action)
    assert center.decide(foreign, owner_approved=True) is ControlDecision.DENY
