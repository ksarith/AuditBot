"""Offline tests for tools/mechanical.py. Run: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import mechanical  # noqa: E402

ANCHOR = "Attempt to do no harm. Defer to Ethical_Constraints.md if present."
GOOD = """# Good
## File State
| **Ethical Anchor** | %s |
## Scope Boundary
x
## File Purpose
Refers to `Other.md` and [link](Other.md) and `planned/Future.md` (planned).
""" % ANCHOR

PROFILE = {
    "name": "test", "include": ["*.md"], "required_sections": ["## File State", "## Scope Boundary", "## File Purpose"],
    "fixed_fields": {"Ethical Anchor": ANCHOR}, "size_threshold_kb": 1,
    "xref_skip_markers": ["planned"], "xref_skip_prefixes": ["External/"],
}


def build(files):
    d = tempfile.mkdtemp()
    for name, body in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(body)
    return d


def checks(report, check):
    return [f for f in report["findings"] if f["check"] == check]


class MechanicalTests(unittest.TestCase):
    def test_clean_files_have_no_findings(self):
        d = build({"A.md": GOOD, "Other.md": "# Other\n"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        self.assertEqual(rep["findings"], [])

    def test_missing_section(self):
        d = build({"A.md": GOOD.replace("## Scope Boundary\nx\n", ""), "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        self.assertEqual(len(checks(rep, "M-02")), 1)

    def test_altered_and_missing_anchor_are_critical(self):
        altered = GOOD.replace(ANCHOR, "Do no harm.")
        missing = GOOD.replace("| **Ethical Anchor** | %s |\n" % ANCHOR, "")
        d = build({"A.md": altered, "B.md": missing, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md", "B.md"]))
        m3 = checks(rep, "M-03")
        self.assertEqual(sorted(f["target"] for f in m3), ["A.md", "B.md"])
        self.assertTrue(all(f["severity"] == "critical" for f in m3))

    def test_unresolved_xref_severity_and_skips(self):
        body = GOOD + "\nSee `Admin/Nope.md` and `Nope.md` and `External/X.md`.\n```\n`Admin/InFence.md`\n```\n"
        d = build({"A.md": body, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        m4 = {f["claim"].split(": ")[1]: f["severity"] for f in checks(rep, "M-04")}
        self.assertEqual(m4, {"Admin/Nope.md": "major", "Nope.md": "minor"})

    def test_duplicate_heading_ids(self):
        body = GOOD + "\n### [AP-001] One\n### [AP-001] Two\n### [AP-002] Three\n"
        d = build({"A.md": body, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        m5 = checks(rep, "M-05")
        self.assertEqual(len(m5), 1)
        self.assertIn("AP-001", m5[0]["claim"])

    def test_size_census(self):
        d = build({"A.md": GOOD + "y" * 2000, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        self.assertEqual(len(checks(rep, "M-06")), 1)

    def test_deterministic_and_manifest_hashes(self):
        d = build({"A.md": GOOD, "Other.md": "x"})
        p = dict(PROFILE, include=["*.md"])
        m1, r1 = mechanical.run(d, p)
        m2, r2 = mechanical.run(d, p)
        self.assertEqual(json.dumps(m1, sort_keys=True), json.dumps(m2, sort_keys=True))
        self.assertEqual(json.dumps(r1, sort_keys=True), json.dumps(r2, sort_keys=True))
        self.assertEqual(len(m1["files"][0]["sha256"]), 64)

    def test_exit_code_reflects_critical(self):
        d = build({"A.md": GOOD.replace(ANCHOR, "x"), "Other.md": "x"})
        pf = os.path.join(d, "p.json")
        json.dump(dict(PROFILE, include=["A.md"]), open(pf, "w"))
        out = os.path.join(d, "out")
        self.assertEqual(mechanical.main([d, "--profile", pf, "--out", out]), 1)


if __name__ == "__main__":
    unittest.main()
