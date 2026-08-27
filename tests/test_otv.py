from versions.otv_solver import VirtualState

def test_virtual_state_initialization():
    state = VirtualState()
    assert state.hops == 0
    assert len(state.recent_sources) == 0
    assert len(state.untrusted_sources) == 0
