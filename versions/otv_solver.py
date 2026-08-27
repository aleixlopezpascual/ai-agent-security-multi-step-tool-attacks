from dataclasses import dataclass, field, replace

@dataclass(frozen=True)
class VirtualState:
    recent_sources: list[str] = field(default_factory=list)
    untrusted_sources: set[str] = field(default_factory=set)
    files_deleted: set[str] = field(default_factory=set)
    files_written: dict[str, str] = field(default_factory=dict)
    emails_sent: list[dict] = field(default_factory=list)
    egress: list[dict] = field(default_factory=list)
    user_intent: set[str] = field(default_factory=set)
    hops: int = 0

def transition(state: VirtualState, action: dict) -> VirtualState | None:
    name = action["name"]
    args = action.get("args", {})
    
    # Simple OptimalGuardrail extraction & sensitive target block emulation
    target = ""
    for key in ["path", "url", "cmd", "data", "body", "content"]:
        if key in args:
            target = str(args[key]).lower()
            break
            
    ultra_dangerous = ["secret", "password", "token", "key", "credential", "private"]
    if target and any(p in target for p in ultra_dangerous):
        return None  # Denied!
        
    # Taint check
    tainted = any(src in ["web", "email"] for src in state.recent_sources)
    dangerous_ops = ["fs.delete", "fs.write", "shell.run", "http.post", "email.send"]
    if tainted and name in dangerous_ops:
        return None  # Denied!

    # Successful state mutation
    next_sources = (state.recent_sources + ["tool"])[-5:]
    next_untrusted = set(state.untrusted_sources)
    if name in ["web.search", "email.read"]:
        next_untrusted.add("web" if "web" in name else "email")
        
    return replace(
        state,
        recent_sources=next_sources,
        untrusted_sources=next_untrusted,
        hops=state.hops + 1
    )
