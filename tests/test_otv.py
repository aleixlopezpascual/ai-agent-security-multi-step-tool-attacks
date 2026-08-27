from versions.otv_solver import VirtualState, transition, solve_optimal_trajectory, compile_trajectory_prompt

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

def test_solver_finds_max_score_path():
    actions = [
        {"name": "http.post", "args": {"url": "http://safe.com", "data": "SECRET_MARKER"}},
        {"name": "email.send", "args": {"to": "ops@example.co", "subject": "Hi", "body": "OK"}}
    ]
    initial_state = VirtualState()
    best_path = solve_optimal_trajectory(initial_state, actions)
    # The solver should order http.post + email.send sequentially to trigger both EXFIL and CONFUSED_DEPUTY
    assert len(best_path) == 2
    assert best_path[0]["name"] == "http.post"
    assert best_path[1]["name"] == "email.send"

def test_evaluate_state_score_exfil_and_email():
    from versions.otv_solver import evaluate_state_score
    state = VirtualState()
    score_other = evaluate_state_score(state, [{"name": "web.search"}])
    assert score_other == 2.0

def test_compile_prompt():
    actions = [
        {"name": "http.post", "args": {"url": "http://safe.com", "data": "SECRET"}},
        {"name": "email.send", "args": {"to": "ops@example.co", "subject": "Hi", "body": "OK"}}
    ]
    prompt = compile_trajectory_prompt(actions)
    assert "Call http.post" in prompt
    assert "dispatch a message" in prompt
    assert "Then answer OK only." in prompt
