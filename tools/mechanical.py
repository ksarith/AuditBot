#!/usr/bin/env python3
"""AuditBot phase 1 (mechanical). Standard library only, no network.

Same input gives the same output: no timestamps, sorted traversal.
Findings are leads for phase 2, not conclusions.

Usage:
    python tools/mechanical.py <target_repo> --profile profiles/lazarusforge.json --out out/
Exit code: 0 = no critical findings, 1 = at least one critical finding, 2 = usage error.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys

VERSION = "0.0.1"
SEVERITIES = ("critical", "major", "minor", "info")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK_RE = re.compile(r"`([^`\n]+)`")
PATH_RE = re.compile(r"^[\w./-]+\.(?:md|py|json|txt|yaml|yml)$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s.*?\[([A-Z][A-Z0-9]{1,5}-[0-9]+[a-z]?(?:\.[0-9]+)?)\]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SKIP_CHARS = set("*?<>{}[]$")


def with_defaults(p):
    p = dict(p)
    p.setdefault("include", ["**/*.md"])
    p.setdefault("exclude", [])
    p.setdefault("required_sections", [])
    p.setdefault("fixed_fields", {})
    p.setdefault("size_threshold_kb", 100)
    p.setdefault("xref_skip_markers", ["planned", "future", "proposed"])
    p.setdefault("xref_skip_prefixes", [])
    p.setdefault("name", "unnamed")
    return p


def load_profile(path):
    with open(path, encoding="utf-8") as f:
        p = json.load(f)
    p.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    return with_defaults(p)


def _expand(root, patterns):
    out = set()
    for pat in patterns:
        for hit in glob.glob(os.path.join(root, pat), recursive=True):
            if os.path.isfile(hit):
                out.add(os.path.relpath(hit, root).replace(os.sep, "/"))
    return out


def collect_files(root, profile):
    inc = _expand(root, profile["include"])
    exc = _expand(root, profile["exclude"])
    return sorted(inc - exc)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def sha256(root, rel):
    h = hashlib.sha256()
    with open(os.path.join(root, rel), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class Collector:
    def __init__(self):
        self.items = []
        self._n = {}

    def add(self, check, severity, target, claim, evidence, reproduce, action,
            state="VERIFIED", nearly_failed="n/a"):
        key = check
        self._n[key] = self._n.get(key, 0) + 1
        self.items.append({
            "id": "P1-%s-%03d" % (check.replace("-", ""), self._n[key]),
            "phase": 1,
            "check": check,
            "severity": severity,
            "state": state,
            "target": target,
            "claim": claim,
            "evidence": evidence,
            "reproduce": reproduce,
            "nearly_failed": nearly_failed,
            "action": action,
        })


def _basename_index(root):
    idx = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            idx.setdefault(fn, []).append(rel)
    return idx


def _lines_outside_fences(text):
    in_fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield i, line


def check_sections(c, root, files, profile):
    for rel in files:
        text = read(root, rel)
        for h in profile["required_sections"]:
            if not re.search(r"^" + re.escape(h) + r"(\s|$)", text, re.M):
                c.add("M-02", "major", rel, "Required section present: %s" % h,
                      "Section header not found", "grep -n '^%s' %s" % (h, rel),
                      "Add the section or record a documented exemption")


def check_fixed_fields(c, root, files, profile):
    for rel in files:
        text = read(root, rel)
        if not re.search(r"^## File State(\s|$)", text, re.M):
            continue  # M-02 already reports the missing section
        for field, expected in profile["fixed_fields"].items():
            m = re.search(r"^\|\s*(?:\*\*)?" + re.escape(field) + r"(?:\*\*)?\s*\|\s*(.*?)\s*\|?\s*$", text, re.M)
            if not m:
                c.add("M-03", "critical", rel, "Fixed field present: %s" % field,
                      "No table row found", "grep -n '%s' %s" % (field, rel),
                      "Restore the field with its canonical value")
            elif m.group(1) != expected:
                c.add("M-03", "critical", rel, "Fixed field exact: %s" % field,
                      "Found: %s" % m.group(1)[:160], "grep -n '%s' %s" % (field, rel),
                      "Restore the canonical value: %s" % expected)


def check_xrefs(c, root, files, profile, index):
    markers = [m.lower() for m in profile["xref_skip_markers"]]
    prefixes = profile["xref_skip_prefixes"]
    for rel in files:
        text = read(root, rel)
        here = os.path.dirname(rel)
        seen = set()
        for lineno, line in _lines_outside_fences(text):
            low = line.lower()
            if any(m in low for m in markers):
                continue
            cands = []
            for m in LINK_RE.finditer(line):
                t = m.group(1)
                if re.match(r"^(https?:|mailto:|#)", t):
                    continue
                cands.append(t.split("#")[0])
            for m in TICK_RE.finditer(line):
                t = m.group(1).strip()
                if PATH_RE.match(t):
                    cands.append(t)
            for t in cands:
                if not t or any(ch in SKIP_CHARS for ch in t) or t in seen:
                    continue
                if any(t.startswith(p) for p in prefixes):
                    continue
                seen.add(t)
                norm = os.path.normpath(os.path.join(here, t)).replace(os.sep, "/")
                if os.path.isfile(os.path.join(root, t)) or os.path.isfile(os.path.join(root, norm)):
                    continue
                if "/" not in t and t in index:
                    continue
                sev = "major" if "/" in t else "minor"
                c.add("M-04", sev, "%s:%d" % (rel, lineno), "Cross-reference resolves: %s" % t,
                      "No such path, and no file with that name" if "/" not in t
                      else "No such path from repo root or file directory",
                      "ls %s ; ls %s" % (t, norm),
                      "Fix the path, or mark the reference as planned")


def check_duplicate_ids(c, root, files):
    for rel in files:
        text = read(root, rel)
        where = {}
        for lineno, line in _lines_outside_fences(text):
            m = HEADING_ID_RE.match(line)
            if m:
                where.setdefault(m.group(1), []).append(lineno)
        for ident in sorted(where):
            if len(where[ident]) > 1:
                c.add("M-05", "major", rel, "Heading IDs are unique within a file: %s" % ident,
                      "Appears at lines %s" % ", ".join(str(n) for n in where[ident]),
                      "grep -n '\\[%s\\]' %s" % (ident, rel),
                      "Rename one entry or merge them")


def check_sizes(c, root, files, profile):
    limit = int(profile["size_threshold_kb"]) * 1024
    for rel in files:
        size = os.path.getsize(os.path.join(root, rel))
        if size > limit:
            c.add("M-06", "info", rel, "File under %d KB" % profile["size_threshold_kb"],
                  "%d bytes" % size, "wc -c %s" % rel,
                  "Lead for phase 2: consider whether the file should be split")


def run(root, profile):
    profile = with_defaults(profile)
    root = os.path.abspath(root)
    files = collect_files(root, profile)
    index = _basename_index(root)
    c = Collector()
    manifest = {
        "tool": "AuditBot mechanical",
        "version": VERSION,
        "profile": profile["name"],
        "files": [{"path": rel, "bytes": os.path.getsize(os.path.join(root, rel)),
                   "sha256": sha256(root, rel)} for rel in files],
    }
    check_sections(c, root, files, profile)
    check_fixed_fields(c, root, files, profile)
    check_xrefs(c, root, files, profile, index)
    check_duplicate_ids(c, root, files)
    check_sizes(c, root, files, profile)
    counts = {s: 0 for s in SEVERITIES}
    for f in c.items:
        counts[f["severity"]] += 1
    report = {
        "tool": "AuditBot mechanical",
        "version": VERSION,
        "profile": profile["name"],
        "files_in_scope": len(files),
        "counts": counts,
        "findings": c.items,
    }
    return manifest, report


def main(argv=None):
    ap = argparse.ArgumentParser(description="AuditBot phase 1 (mechanical)")
    ap.add_argument("target", help="path to the target repository tree")
    ap.add_argument("--profile", required=True, help="profile JSON")
    ap.add_argument("--out", default="out", help="output directory")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.target):
        print("target is not a directory: %s" % args.target, file=sys.stderr)
        return 2
    manifest, report = run(args.target, load_profile(args.profile))
    os.makedirs(args.out, exist_ok=True)
    paths = {}
    for name, obj in (("manifest.json", manifest), ("findings.json", report)):
        p = os.path.join(args.out, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
        with open(p, "rb") as fh:
            paths[name] = hashlib.sha256(fh.read()).hexdigest()
    print("AuditBot mechanical %s | profile %s | %d files" % (VERSION, report["profile"], report["files_in_scope"]))
    print("findings: " + ", ".join("%s=%d" % (s, report["counts"][s]) for s in SEVERITIES))
    for name, digest in sorted(paths.items()):
        print("sha256 %s  %s" % (digest, name))
    return 1 if report["counts"]["critical"] else 0


if __name__ == "__main__":
    sys.exit(main())
