from devintel.modules.plugins import PluginAction, PluginManifest, PluginRisk, PluginService, PluginState

def manifest(pid="video.engine"):
    return PluginManifest(pid, "Video Engine", "1.0.0", "specialist engine", ("generate",), ("tool.execute",))

def test_register_attach_execute():
    s=PluginService(); s.register(manifest()); s.attach("video.engine", lambda a: {"ok": True})
    r=s.execute(PluginAction("video.engine", "generate", "channel-1"))
    assert r.success and r.output == {"ok": True}

def test_high_risk_requires_approval():
    s=PluginService(); s.register(manifest()); s.attach("video.engine", lambda a: "secret")
    action=PluginAction("video.engine", "publish", "channel-1", PluginRisk.HIGH)
    assert not s.execute(action).success
    assert s.execute(action, approved=True).success

def test_failure_isolates_only_plugin():
    s=PluginService(); s.register(manifest()); s.attach("video.engine", lambda a: 1/0)
    r=s.execute(PluginAction("video.engine", "generate", "channel-1"))
    assert not r.success
    assert s.registry.get("video.engine").state == PluginState.ISOLATED

def test_scope_is_data_not_authority():
    s=PluginService(); s.register(manifest()); s.attach("video.engine", lambda a: a.scope_id)
    assert s.execute(PluginAction("video.engine", "generate", "scope-a")).output == "scope-a"

def test_version_replacement_increments_generation():
    s=PluginService(); s.register(manifest()); old=s.registry.get("video.engine").generation
    s.register(PluginManifest("video.engine", "Video Engine", "2.0.0", "specialist engine"))
    assert s.registry.get("video.engine").generation == old+1
