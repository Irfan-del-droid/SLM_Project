"""
detector.py — Language and project type detection for NEXUS Engine
"""
import re


# ── Language detection ─────────────────────────────────────────────────────────

LANG_SIGNATURES = {
    "Python":     [r"\bdef\b", r"\bimport\b", r"\bprint\s*\(", r":\s*$", r"\bself\b"],
    "JavaScript": [r"\bconst\b", r"\blet\b", r"\bvar\b", r"=>\s*{", r"console\.log"],
    "TypeScript": [r":\s*(string|number|boolean|any)\b", r"\binterface\b", r"<T>"],
    "Java":       [r"\bpublic\s+class\b", r"\bSystem\.out", r"void\s+main"],
    "C++":        [r"#include\s*<", r"\bcout\b", r"\bstd::", r"\bnamespace\b"],
    "C":          [r"#include\s*<stdio", r"\bprintf\s*\(", r"\bscanf\s*\("],
    "Go":         [r"\bfunc\b\s+\w+", r"\bfmt\.Print", r"\bpackage\s+main\b"],
    "Rust":       [r"\bfn\s+main\b", r"\blet\s+mut\b", r"\bprintln!\s*\(", r"\buse\s+std"],
    "Bash":       [r"#!/bin/bash", r"\becho\b", r"\$\{", r"\bfi\b"],
    "SQL":        [r"\bSELECT\b", r"\bFROM\b", r"\bWHERE\b", r"\bINSERT\b"],
    "HTML":       [r"<html", r"<div", r"<body", r"<!DOCTYPE"],
    "CSS":        [r"\{[^}]*:\s*[^}]+\}", r"@media", r"\.[\w-]+\s*\{"],
    "R":          [r"\blibrary\s*\(", r"\b<-\b", r"\bggplot\b"],
    "Kotlin":     [r"\bfun\s+main\b", r"\bval\b", r"\bvar\b.*=", r"\bprintln\b"],
    "Swift":      [r"\bvar\b.*:\s*\w+\s*=", r"\bfunc\b", r"print\("],
    "Ruby":       [r"\bdef\b.*\bend\b", r"\bputs\b", r"\brequire\b"],
    "PHP":        [r"<\?php", r"\$\w+\s*=", r"\becho\b"],
    "Dart":       [r"\bvoid\s+main\s*\(", r"\bWidget\b", r"flutter"],
}


def detect_language(code: str, hint: str = "") -> str:
    """Detect programming language from code content and optional hint tag."""
    if hint:
        lang_map = {
            "py": "Python", "python": "Python",
            "js": "JavaScript", "javascript": "JavaScript",
            "ts": "TypeScript", "typescript": "TypeScript",
            "java": "Java", "cpp": "C++", "c": "C",
            "go": "Go", "rust": "Rust", "sh": "Bash", "bash": "Bash",
            "sql": "SQL", "html": "HTML", "css": "CSS",
            "r": "R", "kt": "Kotlin", "kotlin": "Kotlin",
            "swift": "Swift", "rb": "Ruby", "ruby": "Ruby",
            "php": "PHP", "dart": "Dart",
        }
        if hint.lower() in lang_map:
            return lang_map[hint.lower()]

    scores = {}
    for lang, patterns in LANG_SIGNATURES.items():
        score = sum(1 for p in patterns if re.search(p, code, re.MULTILINE | re.IGNORECASE))
        if score > 0:
            scores[lang] = score

    if not scores:
        return "Unknown"
    return max(scores, key=scores.get)


# ── Project type detection ─────────────────────────────────────────────────────

PROJECT_SIGNATURES = {
    "Streamlit App":   [r"\bstreamlit\b", r"\bst\.\w+", r"st\.title", r"st\.chat"],
    "REST API":        [r"\bfastapi\b", r"\bflask\b", r"\bdjango\b", r"@app\.route", r"\brouter\b"],
    "CLI Tool":        [r"\bargparse\b", r"\bclick\b", r"\btyper\b", r"sys\.argv"],
    "ML / AI":         [r"\bpandas\b", r"\bnumpy\b", r"\bsklearn\b", r"\btorch\b", r"\btensorflow\b", r"\bmodel\.fit\b"],
    "Web Frontend":    [r"<html", r"\breact\b", r"\bvue\b", r"\bsvelte\b", r"document\."],
    "Database":        [r"\bSELECT\b", r"\bINSERT\b", r"\bsqlalchemy\b", r"\bpsycopg\b"],
    "Script / Utility":[r"if __name__\s*==\s*['\"]__main__['\"]", r"\bos\.path\b", r"\bshutil\b"],
    "Package / Library":[r"\bsetup\.py\b", r"\bpyproject\.toml\b", r"\b__init__\.py\b"],
    "Game":            [r"\bpygame\b", r"\bphaser\b", r"\bunity\b"],
    "Desktop App":     [r"\btkinter\b", r"\bpyqt\b", r"\bwxpython\b"],
}


def detect_project_type(response_text: str, code: str) -> str:
    """Detect project type from response text and code."""
    combined = (response_text + " " + code).lower()
    scores = {}
    for ptype, patterns in PROJECT_SIGNATURES.items():
        score = sum(1 for p in patterns if re.search(p, combined, re.IGNORECASE))
        if score > 0:
            scores[ptype] = score

    if not scores:
        return "General Code"
    return max(scores, key=scores.get)