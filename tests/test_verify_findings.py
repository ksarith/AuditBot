"""Offline tests for tools/verify_findings.py."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import mechanical  # noqa: E402
import verify_findings as vf  # noqa: E402

def quiet(fn, *a):
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


DOC = "# Title\nThe pump runs at 40 W.\nIt has two modes:\n  idle and active.\nEnd.\n"


def setup():
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "A.md"), "w") as f:
        f.write(DOC)
    with open(os.path.join(d, "B.md"), "w") as f:
        f.write("# B\n")
    manifest, _ = mechanical.run(d, {"name": "t", "include": ["*.md"]})
    return d, manifest


def finding(fid, refs, **kw):
    return dict({"id": fid, "phase": 2, "evidence_ref": refs}, **kw)


def status(report, fid):
    return next(r["status"] for r in report["results"] if r["id"] == fid)


class VerifyTests(unittest.TestCase):
    def test_statuses(self):
        d, m = setup()
        fs = [
            finding("ok", [{"file": "A.md", "lines": "2", "quote": "pump runs at 40 W"}]),
            finding("multi-line", [{"file": "A.md", "lines": "3-4", "quote": "two modes: idle and active"}]),
            finding("ellipsis", [{"file": "A.md", "lines": "2-4", "quote": "pump ... idle and active"}]),
            finding("bad-quote", [{"file": "A.md", "lines": "2", "quote": "pump runs at 50 W"}]),
            finding("wrong-lines", [{"file": "A.md", "lines": "5", "quote": "pump runs"}]),
            finding("out-of-range", [{"file": "A.md", "lines": "40-41", "quote": "x"}]),
            finding("not-in-manifest", [{"file": "C.md", "lines": "1", "quote": "x"}]),
            finding("bad-ref", [{"file": "A.md", "lines": "x", "quote": "x"}]),
            finding("none", []),
            finding("explained", [], no_evidence_reason="Omission finding: nothing to cite"),
            {"id": "p1", "phase": 1},
            finding("one-bad-one-good", [{"file": "A.md", "lines": "2", "quote": "pump"},
                                         {"file": "A.md", "lines": "2", "quote": "nonsense"}]),
        ]
        rep = vf.verify(d, m, fs)
        expect = {"ok": "VERIFIED", "multi-line": "VERIFIED", "ellipsis": "VERIFIED",
                  "bad-quote": "QUOTE_NOT_FOUND", "wrong-lines": "QUOTE_NOT_FOUND",
                  "out-of-range": "LINES_OUT_OF_RANGE", "not-in-manifest": "FILE_NOT_IN_MANIFEST",
                  "bad-ref": "BAD_REF", "none": "NO_EVIDENCE_REF", "explained": "NO_EVIDENCE_EXPLAINED",
                  "p1": "SKIPPED_PHASE1", "one-bad-one-good": "QUOTE_NOT_FOUND"}
        for fid, st in expect.items():
            self.assertEqual(status(rep, fid), st, fid)

    def test_hash_mismatch_detects_target_drift(self):
        d, m = setup()
        with open(os.path.join(d, "A.md"), "a") as f:
            f.write("changed\n")
        rep = vf.verify(d, m, [finding("x", [{"file": "A.md", "lines": "2", "quote": "pump"}])])
        self.assertEqual(status(rep, "x"), "HASH_MISMATCH")

    def test_coverage_is_reported_not_proven(self):
        d, m = setup()
        rep = vf.verify(d, m, [finding("x", [{"file": "A.md", "lines": "2", "quote": "pump"}])])
        self.assertEqual(rep["coverage"]["not_cited"], ["B.md"])
        self.assertIn("not proof", rep["coverage"]["note"])

    def test_cli_exit_codes_and_errors(self):
        d, m = setup()
        mp, fp, op = (os.path.join(d, n) for n in ("m.json", "f.json", "v.json"))
        dump(mp, m)
        dump(fp, {"findings": [finding("x", [{"file": "A.md", "lines": "2", "quote": "pump"}])]})
        self.assertEqual(quiet(vf.main, [d, "--manifest", mp, "--findings", fp, "--out", op]), 0)
        dump(fp, [finding("x", [{"file": "A.md", "lines": "2", "quote": "nope"}])])
        self.assertEqual(quiet(vf.main, [d, "--manifest", mp, "--findings", fp, "--out", op]), 1)
        self.assertEqual(quiet(vf.main, [d, "--manifest", os.path.join(d, "missing.json"), "--findings", fp, "--out", op]), 2)

    def test_empty_manifest_fails_closed(self):
        d, _ = setup()
        with self.assertRaises(vf.VerifyError):
            vf.verify(d, {"files": []}, [])


if __name__ == "__main__":
    unittest.main()
