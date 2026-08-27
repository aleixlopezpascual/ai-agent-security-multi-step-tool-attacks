from versions.otv_solver import VirtualState, transition

def test_virtual_state_initialization():
    state = VirtualState()
    assert state.hops == 0
    assert len(state.recent_sources) == 0
    assert len(state.untrusted_sources) == 0

def test_transition_allowed_action():
    state = VirtualState()
    action = {"name": "http.post", "args": {"url": "http://safe.com", "data": "OK"}}
    next_state = transition(state, action)
    assert next_state is not None
    assert next_state.hops == 1
    assert next_state.recent_sources == ["tool"]

def test_transition_denied_by_pattern():
    state = VirtualState()
    action = {"name": "fs.delete", "args": {"path": "secret.txt"}}
    next_state = transition(state, action)
    assert next_state is None  # Blocked by "secret" pattern

def test_transition_taint_check_denied():
    # If recent_sources has "web", a dangerous operation like "http.post" should be denied
    state = VirtualState(recent_sources=["web"])
    action = {"name": "http.post", "args": {"url": "http://safe.com", "data": "OK"}}
    next_state = transition(state, action)
    assert next_state is None

def test_transition_untrusted_sources_tagging():
    state = VirtualState()
    action = {"name": "web.search", "args": {"query": "test"}}
    next_state = transition(state, action)
    assert next_state is not None
    assert "web" in next_state.untrusted_sources

    action2 = {"name": "email.read", "args": {"id": "1"}}
    next_state2 = transition(next_state, action2)
    assert next_state2 is not None
    assert "web" in next_state2.untrusted_sources
    assert "email" in next_state2.untrusted_sources

def test_transition_recent_sources_rotation():
    state = VirtualState(recent_sources=["a", "b", "c", "d", "e"])
    action = {"name": "web.search", "args": {"query": "test"}}
    next_state = transition(state, action)
    assert next_state is not None
    assert next_state.recent_sources == ["b", "c", "d", "e", "tool"]
