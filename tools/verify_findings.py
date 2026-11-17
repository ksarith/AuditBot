#!/usr/bin/env python3
"""AuditBot citation verifier. Standard library only, no network.

Checks that the evidence a phase 2 or phase 3 finding cites actually exists:
the file is in the manifest, the file still matches its recorded hash, the
line range exists, and the quoted text appears in those lines.

It does NOT judge whether a finding is right, and it cannot prove that an
agent examined anything. It proves that the citations are real.

Usage:
    python tools/verify_findings.py <target_repo> --manifest out/manifest.json \
        --findings p2_findings.json --out out/verification.json

Finding fields used (see templates/finding.md):
    id, phase, evidence_ref: [{"file": "...", "lines": "12-18", "quote": "..."}]
    no_evidence_reason: required when evidence_ref is empty

Exit codes: 0 all citations verified, 1 at least one failure, 2 error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

VERSION = "0.0.3"
LONG_QUOTE = 400
OK = {"VERIFIED", "NO_EVIDENCE_EXPLAINED", "SKIPPED_PHASE1"}


class VerifyError(Exception):
    pass


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _load_json(path, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise VerifyError("cannot read %s %s: %s" % (what, path, e))


def parse_lines(spec):
    if isinstance(spec, int) and not isinstance(spec, bool):
        return (spec, spec) if spec >= 1 else None
    if isinstance(spec, str):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", spec)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            if 1 <= a <= b:
                return a, b
    return None


def _segments(quote):
    """Non-empty quote segments, split on '...' or the ellipsis character."""
    return [g for g in (_norm(x) for x in re.split(r"\.\.\.|\u2026", quote)) if g]


def _quote_in(text, quote):
    """Quote segments must appear in order. A quote with no segment never matches."""
    segs = _segments(quote)
    if not segs:
        return False
    pos = 0
    text = _norm(text)
    for seg in segs:
        i = text.find(seg, pos)
        if i < 0:
            return False
        pos = i + len(seg)
    return True


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_ref(root, by_path, ref):
    if not isinstance(ref, dict) or not all(k in ref for k in ("file", "lines", "quote")):
        return "BAD_REF", "evidence_ref entries need file, lines and quote"
    rel = str(ref["file"]).replace("\\", "/")
    if rel not in by_path:
        return "FILE_NOT_IN_MANIFEST", rel
    full = os.path.join(root, rel)
    if os.path.islink(full) or not os.path.isfile(full):
        return "FILE_NOT_IN_MANIFEST", "%s is missing or a symlink" % rel
    if _sha(full) != by_path[rel]:
        return "HASH_MISMATCH", "%s changed since the manifest was written" % rel
    rng = parse_lines(ref["lines"])
    if rng is None:
        return "BAD_REF", "lines must be 'N' or 'N-M'"
    quote = ref["quote"]
    if not isinstance(quote, str) or not _segments(quote):
        return "BAD_REF", "quote must contain text outside ellipses"
    with open(full, encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    a, b = rng
    if b > len(lines):
        return "LINES_OUT_OF_RANGE", "%s has %d lines; cited %d-%d" % (rel, len(lines), a, b)
    if not _quote_in(" ".join(lines[a - 1:b]), quote):
        return "QUOTE_NOT_FOUND", "quote not found in %s lines %d-%d" % (rel, a, b)
    note = " (long quote)" if len(quote) > LONG_QUOTE else ""
    return "VERIFIED", note


def verify(root, manifest, findings):
    by_path = {e["path"]: e["sha256"] for e in manifest.get("files", [])}
    if not by_path:
        raise VerifyError("manifest lists no files")
    results, cited = [], set()
    for f in findings:
        fid = f.get("id", "(no id)")
        if f.get("phase") == 1:
            results.append({"id": fid, "status": "SKIPPED_PHASE1", "refs": []})
            continue
        refs = f.get("evidence_ref")
        if not refs:
            reason = f.get("no_evidence_reason")
            status = "NO_EVIDENCE_EXPLAINED" if isinstance(reason, str) and reason.strip() else "NO_EVIDENCE_REF"
            results.append({"id": fid, "status": status, "refs": []})
            continue
        if not isinstance(refs, list):
            results.append({"id": fid, "status": "BAD_REF", "refs": [{"status": "BAD_REF", "detail": "evidence_ref must be a list"}]})
            continue
        out, worst = [], "VERIFIED"
        for r in refs:
            st, detail = verify_ref(root, by_path, r)
            out.append({"file": r.get("file") if isinstance(r, dict) else None,
                        "lines": r.get("lines") if isinstance(r, dict) else None,
                        "status": st, "detail": detail})
            if st != "VERIFIED" and worst == "VERIFIED":
                worst = st
            if st == "VERIFIED":
                cited.add(str(r["file"]).replace("\\", "/"))
        results.append({"id": fid, "status": worst, "refs": out})
    summary = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    coverage = {"files_in_manifest": len(by_path), "files_cited": len(cited),
                "not_cited": sorted(set(by_path) - cited),
                "note": "Coverage is a report, not proof of examination."}
    return {"tool": "AuditBot verify_findings", "version": VERSION, "vacuous": not results,
            "summary": summary, "coverage": coverage, "results": results}


def main(argv=None):
    ap = argparse.ArgumentParser(description="AuditBot citation verifier")
    ap.add_argument("target")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--out", default="verification.json")
    ap.add_argument("--allow-empty", action="store_true",
                    help="exit 0 on an empty findings list (the report is marked vacuous)")
    args = ap.parse_args(argv)
    try:
        if not os.path.isdir(args.target):
            raise VerifyError("target is not a directory: %s" % args.target)
        manifest = _load_json(args.manifest, "manifest")
        data = _load_json(args.findings, "findings")
        findings = data.get("findings") if isinstance(data, dict) else data
        if not isinstance(findings, list):
            raise VerifyError("findings file must be a list or an object with a 'findings' list")
        if not findings and not args.allow_empty:
            raise VerifyError("findings list is empty: nothing was verified (use --allow-empty to accept a phase that found nothing)")
        report = verify(os.path.abspath(args.target), manifest, findings)
    except VerifyError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    print("AuditBot verify_findings %s | %d findings" % (VERSION, len(report["results"])))
    if report["vacuous"]:
        print("VACUOUS: no findings were verified")
    print("summary: " + ", ".join("%s=%d" % kv for kv in sorted(report["summary"].items())))
    cov = report["coverage"]
    print("coverage: %d of %d manifest files cited (a report, not proof)" % (cov["files_cited"], cov["files_in_manifest"]))
    return 0 if all(r["status"] in OK for r in report["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
