"""
complexity.py — Code complexity analyzer for NEXUS Engine
"""
import re


def analyze_complexity(code: str) -> dict:
    """
    Estimate code complexity by detecting loops, functions, and conditions.
    Returns a dict with counts and a level label.
    """
    if not code:
        return {"loops": 0, "functions": 0, "conditions": 0, "level": "Unknown", "score": 0}

    lines = code.splitlines()

    # ── Pattern matching ──────────────────────────────────────────────────────
    loop_patterns = [
        r"\bfor\b", r"\bwhile\b", r"\bforeach\b", r"\bloop\b",
        r"\.forEach\b", r"\.map\b", r"\.filter\b", r"\.reduce\b",
        r"\bdo\s*{", r"\.for_each\b",
    ]
    function_patterns = [
        r"\bdef\b", r"\bfn\b", r"\bfunc\b", r"\bfunction\b",
        r"\bvoid\b\s+\w+\s*\(", r"\bpub\s+fn\b",
        r"=>\s*{", r":\s*Callable",
    ]
    condition_patterns = [
        r"\bif\b", r"\belif\b", r"\belse\b", r"\bswitch\b",
        r"\bmatch\b", r"\bcase\b", r"\bternary\b", r"\?\s*\w",
        r"\btry\b", r"\bcatch\b", r"\bexcept\b",
    ]
    class_patterns = [r"\bclass\b", r"\bstruct\b", r"\btrait\b", r"\binterface\b"]
    recursion_patterns = [r"def\s+(\w+)[^:]*:[\s\S]*?\1\s*\("]  # rough

    def count_patterns(patterns):
        total = 0
        for line in lines:
            for p in patterns:
                total += len(re.findall(p, line))
        return total

    loops      = count_patterns(loop_patterns)
    functions  = count_patterns(function_patterns)
    conditions = count_patterns(condition_patterns)
    classes    = count_patterns(class_patterns)
    loc        = len([l for l in lines if l.strip() and not l.strip().startswith(("#","//","/*","*","\"\"\"","'''"))])

    # ── Scoring ────────────────────────────────────────────────────────────────
    score = loops * 3 + functions * 2 + conditions * 1.5 + classes * 4 + loc * 0.05

    if score < 10:
        level = "Beginner"
    elif score < 30:
        level = "Intermediate"
    else:
        level = "Advanced"

    return {
        "loops":      loops,
        "functions":  functions,
        "conditions": conditions,
        "classes":    classes,
        "loc":        loc,
        "score":      round(score, 1),
        "level":      level,
    }