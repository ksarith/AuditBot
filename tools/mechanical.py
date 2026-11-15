#!/usr/bin/env python3
"""AuditBot phase 1 (mechanical). Standard library only, no network.

Same input gives the same output: no timestamps, sorted traversal.
Findings are leads for phase 2, not conclusions.

Usage:
    python tools/mechanical.py <target_repo> --profile profiles/lazarusforge.json --out out/

Exit codes:
    0  no critical and no major findings
    1  at least one critical finding
    2  error: bad usage, bad profile, or nothing in scope (fail closed)
    3  major findings, no critical
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import hashlib
import json
import os
import re
import sys

VERSION = "0.0.2"
SEVERITIES = ("critical", "major", "minor", "info")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK_RE = re.compile(r"`([^`\n]+)`")
PATH_RE = re.compile(r"^[\w./-]+\.(?:md|py|json|txt|yaml|yml)$")
HEADING_ID_RE = re.compile(r"^#{1,6}\s.*?\[([A-Z][A-Z0-9]{1,5}-[0-9]+[a-z]?(?:\.[0-9]+)?)\]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SKIP_CHARS = set("*?<>{}[]$")

LIST_KEYS = ("include", "exclude", "required_sections", "xref_skip_markers",
             "xref_skip_prefixes", "id_cross_file_ignore")
ALLOWED_KEYS = set(LIST_KEYS) | {"name", "description", "fixed_fields",
                                 "size_threshold_kb", "xref_basename_fallback"}


class AuditError(Exception):
    """Configuration or scope problem. The tool fails closed instead of reporting 'clean'."""


# ---------------------------------------------------------------- profile

def with_defaults(p):
    if not isinstance(p, dict):
        raise AuditError("profile must be a JSON object")
    unknown = sorted(set(p) - ALLOWED_KEYS)
    if unknown:
        raise AuditError("unknown profile key(s): %s. Allowed: %s"
                         % (", ".join(unknown), ", ".join(sorted(ALLOWED_KEYS))))
    p = dict(p)
    p.setdefault("include", ["**/*.md"])
    p.setdefault("exclude", [])
    p.setdefault("required_sections", [])
    p.setdefault("fixed_fields", {})
    p.setdefault("size_threshold_kb", 100)
    p.setdefault("xref_skip_markers", ["planned", "future", "proposed"])
    p.setdefault("xref_skip_prefixes", [])
    p.setdefault("id_cross_file_ignore", [])
    p.setdefault("xref_basename_fallback", "off")
    p.setdefault("name", "unnamed")
    p.setdefault("description", "")
    for k in LIST_KEYS:
        if not isinstance(p[k], list) or not all(isinstance(x, str) for x in p[k]):
            raise AuditError("profile key '%s' must be a list of strings" % k)
    if not p["include"]:
        raise AuditError("profile key 'include' must not be empty")
    ff = p["fixed_fields"]
    if not isinstance(ff, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in ff.items()):
        raise AuditError("profile key 'fixed_fields' must map strings to strings")
    t = p["size_threshold_kb"]
    if isinstance(t, bool) or not isinstance(t, (int, float)) or t <= 0:
        raise AuditError("profile key 'size_threshold_kb' must be a positive number")
    if p["xref_basename_fallback"] not in ("off", "unique"):
        raise AuditError("profile key 'xref_basename_fallback' must be 'off' or 'unique'")
    if not isinstance(p["name"], str) or not isinstance(p["description"], str):
        raise AuditError("profile keys 'name' and 'description' must be strings")
    return p


def load_profile(path):
    try:
        with open(path, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, ValueError) as e:
        raise AuditError("cannot read profile %s: %s" % (path, e))
    if isinstance(p, dict):
        p.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    return with_defaults(p)


# ---------------------------------------------------------------- scope

def _is_linked(root, rel):
    """True if any component of rel (below root) is a symlink."""
    cur = root
    for part in rel.split("/"):
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            return True
    return False


def _expand(root, patterns):
    out = set()
    for pat in patterns:
        for hit in glob.glob(os.path.join(root, pat), recursive=True):
            rel = os.path.relpath(hit, root).replace(os.sep, "/")
            if os.path.isfile(hit) or os.path.islink(hit):
                out.add(rel)
    return out


def collect_files(root, profile):
    """Return (files, skipped_symlinks). Symlinks are never followed or hashed."""
    inc = _expand(root, profile["include"])
    exc = _expand(root, profile["exclude"])
    chosen = sorted(inc - exc)
    files, skipped = [], []
    for rel in chosen:
        if _is_linked(root, rel):
            skipped.append(rel)
        elif os.path.isfile(os.path.join(root, rel)):
            files.append(rel)
    return files, skipped


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
        self._n[check] = self._n.get(check, 0) + 1
        self.items.append({
            "id": "P1-%s-%03d" % (check.replace("-", ""), self._n[check]),
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

    def count(self, check):
        return sum(1 for f in self.items if f["check"] == check)


def _basename_index(root):
    idx = {}
    for dirpath, dirnames, filenames in os.walk(root):  # does not follow directory symlinks
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            if os.path.islink(full):
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
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


# ---------------------------------------------------------------- checks

def check_sections(c, root, files, profile):
    for rel in files:
        text = read(root, rel)
        for h in profile["required_sections"]:
            if not re.search(r"^" + re.escape(h) + r"(\s|$)", text, re.M):
                c.add("M-02", "major", rel, "Required section present: %s" % h,
                      "Section header not found", "grep -n '^%s' %s" % (h, rel),
                      "Add the section or record a documented exemption")


def check_fixed_fields(c, root, files, profile):
    examined = 0
    for rel in files:
        text = read(root, rel)
        if not re.search(r"^## File State(\s|$)", text, re.M):
            continue  # M-02 already reports the missing section
        examined += 1
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
    return examined


def _resolve(root, here, t, index, mode):
    """Return ('ok'|'missing'|'ambiguous'|'escapes', extra)."""
    if os.path.isabs(t):
        return "escapes", None
    norm = os.path.normpath(os.path.join(here, t)).replace(os.sep, "/")
    if norm == ".." or norm.startswith("../"):
        return "escapes", None
    for cand in (t, norm):
        cand = os.path.normpath(cand).replace(os.sep, "/")
        if os.path.isfile(os.path.join(root, cand)) and not _is_linked(root, cand):
            return "ok", None
    if "/" not in t and mode == "unique":
        hits = index.get(t, [])
        if len(hits) == 1:
            return "ok", None
        if len(hits) > 1:
            return "ambiguous", hits
    return "missing", None


def check_xrefs(c, root, files, profile, index):
    markers = [m.lower() for m in profile["xref_skip_markers"]]
    prefixes = profile["xref_skip_prefixes"]
    mode = profile["xref_basename_fallback"]
    stats = {"refs_checked": 0, "refs_skipped_by_marker": 0, "refs_skipped_by_prefix": 0}
    for rel in files:
        text = read(root, rel)
        here = os.path.dirname(rel)
        seen = set()
        for lineno, line in _lines_outside_fences(text):
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
            cands = [t for t in cands if t and not any(ch in SKIP_CHARS for ch in t)]
            if cands and any(m in line.lower() for m in markers):
                stats["refs_skipped_by_marker"] += len(cands)
                continue
            for t in cands:
                if t in seen:
                    continue
                seen.add(t)
                if any(t.startswith(p) for p in prefixes):
                    stats["refs_skipped_by_prefix"] += 1
                    continue
                stats["refs_checked"] += 1
                where = "%s:%d" % (rel, lineno)
                status, extra = _resolve(root, here, t, index, mode)
                if status == "ok":
                    continue
                if status == "escapes":
                    c.add("M-04", "major", where, "Cross-reference stays inside the target: %s" % t,
                          "Path points outside the target root (not checked further)",
                          "inspect line %d of %s" % (lineno, rel),
                          "Fix the path, or confirm the reference is intentionally external")
                elif status == "ambiguous":
                    c.add("M-04", "minor", where, "Cross-reference is unambiguous: %s" % t,
                          "%d files share this name: %s" % (len(extra), ", ".join(extra[:3])),
                          "find . -name '%s'" % t,
                          "Use a folder-qualified path")
                else:
                    sev = "major" if "/" in t else "minor"
                    c.add("M-04", sev, where, "Cross-reference resolves: %s" % t,
                          "No such path from repo root or file directory" if "/" in t
                          else "No such path from repo root or file directory"
                               + ("" if mode == "unique" else " (name-only fallback is off)"),
                          "ls %s ; ls %s" % (t, os.path.normpath(os.path.join(here, t))),
                          "Fix the path, or mark the reference as planned")
    return stats


def check_duplicate_ids(c, root, files, profile):
    ids_seen = 0
    by_id = {}  # id -> {rel: [lines]}
    for rel in files:
        text = read(root, rel)
        for lineno, line in _lines_outside_fences(text):
            m = HEADING_ID_RE.match(line)
            if m:
                ids_seen += 1
                by_id.setdefault(m.group(1), {}).setdefault(rel, []).append(lineno)
    ignore = profile["id_cross_file_ignore"]
    for ident in sorted(by_id):
        files_for = by_id[ident]
        for rel in sorted(files_for):
            if len(files_for[rel]) > 1:
                c.add("M-05", "major", rel, "Heading IDs are unique within a file: %s" % ident,
                      "Appears at lines %s" % ", ".join(str(n) for n in files_for[rel]),
                      "grep -n '\\[%s\\]' %s" % (ident, rel),
                      "Rename one entry or merge them")
        cross = [r for r in sorted(files_for) if not any(fnmatch.fnmatch(r, g) for g in ignore)]
        if len(cross) > 1:
            c.add("M-05", "minor", cross[0], "Heading ID appears in one file only: %s" % ident,
                  "Also in: %s" % ", ".join("%s:%d" % (r, files_for[r][0]) for r in cross[1:4]),
                  "grep -rn '\\[%s\\]' ." % ident,
                  "Check whether this is an intended mirror (use id_cross_file_ignore) or a collision")
    return ids_seen


def check_sizes(c, root, files, profile):
    limit = float(profile["size_threshold_kb"]) * 1024
    for rel in files:
        size = os.path.getsize(os.path.join(root, rel))
        if size > limit:
            c.add("M-06", "info", rel, "File under %s KB" % profile["size_threshold_kb"],
                  "%d bytes" % size, "wc -c %s" % rel,
                  "Lead for phase 2: consider whether the file should be split")


def check_symlinks(c, skipped):
    for rel in skipped:
        c.add("M-07", "info", rel, "In-scope path is not a symlink",
              "Symlink not followed, not hashed, not read", "ls -l %s" % rel,
              "Inspect manually; AuditBot never follows symlinks")


# ---------------------------------------------------------------- run

def run(root, profile):
    profile = with_defaults(profile)
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise AuditError("target is not a directory: %s" % root)
    files, skipped = collect_files(root, profile)
    if not files:
        raise AuditError("no files in scope: include patterns %s matched nothing (symlinks skipped: %d)"
                         % (profile["include"], len(skipped)))
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
    ff_examined = check_fixed_fields(c, root, files, profile)
    xstats = check_xrefs(c, root, files, profile, index)
    ids_seen = check_duplicate_ids(c, root, files, profile)
    check_sizes(c, root, files, profile)
    check_symlinks(c, skipped)

    n = len(files)
    checks_run = {
        "M-01": {"enabled": True, "files_examined": n},
        "M-02": {"enabled": bool(profile["required_sections"]),
                 "config": {"required_sections": profile["required_sections"]},
                 "files_examined": n if profile["required_sections"] else 0},
        "M-03": {"enabled": bool(profile["fixed_fields"]),
                 "config": {"fields": sorted(profile["fixed_fields"])},
                 "files_examined": ff_examined},
        "M-04": dict({"enabled": True, "files_examined": n,
                      "config": {"basename_fallback": profile["xref_basename_fallback"],
                                 "skip_markers": profile["xref_skip_markers"],
                                 "skip_prefixes": profile["xref_skip_prefixes"]}}, **xstats),
        "M-05": {"enabled": True, "files_examined": n, "ids_seen": ids_seen,
                 "config": {"id_cross_file_ignore": profile["id_cross_file_ignore"]}},
        "M-06": {"enabled": True, "files_examined": n,
                 "config": {"size_threshold_kb": profile["size_threshold_kb"]}},
        "M-07": {"enabled": True, "symlinks_skipped": len(skipped)},
    }
    for cid, entry in checks_run.items():
        entry["findings"] = c.count(cid)
        if not entry["enabled"]:
            entry["reason"] = "not configured in profile"
    counts = {s: 0 for s in SEVERITIES}
    for f in c.items:
        counts[f["severity"]] += 1
    report = {
        "tool": "AuditBot mechanical",
        "version": VERSION,
        "profile": profile["name"],
        "scope": {"include": profile["include"], "exclude": profile["exclude"],
                  "files_in_scope": n, "symlinks_skipped": skipped},
        "checks_run": checks_run,
        "counts": counts,
        "findings": c.items,
    }
    return manifest, report


def exit_code(report):
    if report["counts"]["critical"]:
        return 1
    if report["counts"]["major"]:
        return 3
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="AuditBot phase 1 (mechanical)")
    ap.add_argument("target", help="path to the target repository tree")
    ap.add_argument("--profile", required=True, help="profile JSON")
    ap.add_argument("--out", default="out", help="output directory")
    args = ap.parse_args(argv)
    try:
        manifest, report = run(args.target, load_profile(args.profile))
    except AuditError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    os.makedirs(args.out, exist_ok=True)
    paths = {}
    for name, obj in (("manifest.json", manifest), ("findings.json", report)):
        p = os.path.join(args.out, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
        with open(p, "rb") as fh:
            paths[name] = hashlib.sha256(fh.read()).hexdigest()
    print("AuditBot mechanical %s | profile %s | %d files" % (VERSION, report["profile"], report["scope"]["files_in_scope"]))
    print("findings: " + ", ".join("%s=%d" % (s, report["counts"][s]) for s in SEVERITIES))
    off = [k for k, v in report["checks_run"].items() if not v["enabled"]]
    if off:
        print("checks not run: " + ", ".join(off))
    if report["scope"]["symlinks_skipped"]:
        print("symlinks skipped: %d" % len(report["scope"]["symlinks_skipped"]))
    for name, digest in sorted(paths.items()):
        print("sha256 %s  %s" % (digest, name))
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
