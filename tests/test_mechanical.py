"""Offline tests for tools/mechanical.py. Run: python -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import mechanical  # noqa: E402

def quiet(fn, *a):
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


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
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
    return d


def checks(report, check):
    return [f for f in report["findings"] if f["check"] == check]


class Phase1Checks(unittest.TestCase):
    def test_clean_files_have_no_findings(self):
        d = build({"A.md": GOOD, "Other.md": "# Other\n"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        self.assertEqual(rep["findings"], [])
        self.assertEqual(mechanical.exit_code(rep), 0)

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
        self.assertEqual(mechanical.exit_code(rep), 1)

    def test_unresolved_xref_severity_and_skips(self):
        body = GOOD + "\nSee `Admin/Nope.md` and `Nope.md` and `External/X.md`.\n```\n`Admin/InFence.md`\n```\n"
        d = build({"A.md": body, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        m4 = {f["claim"].split(": ")[1]: f["severity"] for f in checks(rep, "M-04")}
        self.assertEqual(m4, {"Admin/Nope.md": "major", "Nope.md": "minor"})

    def test_xref_escaping_root_is_flagged_not_probed(self):
        d = build({"A.md": GOOD + "\nSee `../outside.md`.\n", "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md"]))
        m4 = checks(rep, "M-04")
        self.assertEqual(len(m4), 1)
        self.assertIn("outside the target root", m4[0]["evidence"])

    def test_relative_paths_inside_root_resolve(self):
        d = build({"sub/A.md": GOOD + "\nSee `../Other.md` and `...-candB.md` and [x](../Other.md).\n", "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["sub/A.md"]))
        m4 = checks(rep, "M-04")
        # `../Other.md` resolves from sub/; the ellipsis-led token is just an unresolved bare name, not an escape
        self.assertEqual([(f["severity"], f["claim"].split(": ")[1]) for f in m4], [("minor", "...-candB.md")])

    def test_duplicate_filenames_name_fallback_modes(self):
        files = {"A.md": GOOD + "\nSee `Notes.md`.\n", "Other.md": "x", "docs/Notes.md": "x", "old/Notes.md": "x"}
        d = build(files)
        _, off = mechanical.run(d, dict(PROFILE, include=["A.md"], xref_basename_fallback="off"))
        _, uni = mechanical.run(d, dict(PROFILE, include=["A.md"], xref_basename_fallback="unique"))
        self.assertIn("fallback is off", checks(off, "M-04")[0]["evidence"])
        self.assertIn("2 files share this name", checks(uni, "M-04")[0]["evidence"])
        d2 = build({"A.md": GOOD + "\nSee `Notes.md`.\n", "Other.md": "x", "docs/Notes.md": "x"})
        _, one = mechanical.run(d2, dict(PROFILE, include=["A.md"], xref_basename_fallback="unique"))
        self.assertEqual(checks(one, "M-04"), [])

    def test_duplicate_heading_ids_within_and_across_files(self):
        a = GOOD + "\n### [AP-001] One\n### [AP-001] Two\n### [AP-002] Three\n"
        b = "# B\n### [AP-002] Elsewhere\n"
        d = build({"A.md": a, "B.md": b, "Other.md": "x"})
        _, rep = mechanical.run(d, dict(PROFILE, include=["A.md", "B.md"], required_sections=[], fixed_fields={}))
        sev = {(f["severity"], f["claim"].split(": ")[1]) for f in checks(rep, "M-05")}
        self.assertEqual(sev, {("major", "AP-001"), ("minor", "AP-002")})
        _, ign = mechanical.run(d, dict(PROFILE, include=["A.md", "B.md"], required_sections=[], fixed_fields={},
                                        id_cross_file_ignore=["B.md"]))
        self.assertEqual({f["severity"] for f in checks(ign, "M-05")}, {"major"})

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
        self.assertNotIn("findings", json.dumps(m1))  # manifest records inputs only

    def test_unicode_paths(self):
        d = build({"Docs/R\u00e9sum\u00e9.md": "# x\n"})
        m, _ = mechanical.run(d, {"name": "t", "include": ["**/*.md"]})
        self.assertEqual([f["path"] for f in m["files"]], ["Docs/R\u00e9sum\u00e9.md"])


class FailClosed(unittest.TestCase):
    def test_unknown_profile_key_is_an_error(self):
        with self.assertRaises(mechanical.AuditError) as cm:
            mechanical.with_defaults({"name": "t", "required_section": ["## X"]})
        self.assertIn("required_section", str(cm.exception))

    def test_wrong_types_are_errors(self):
        for bad in ({"include": "A.md"}, {"fixed_fields": ["x"]}, {"size_threshold_kb": 0},
                    {"xref_basename_fallback": "maybe"}, {"include": []}):
            with self.assertRaises(mechanical.AuditError, msg=str(bad)):
                mechanical.with_defaults(bad)

    def test_empty_scope_is_an_error(self):
        with self.assertRaises(mechanical.AuditError):
            mechanical.run(build({}), {"name": "t", "include": ["**/*.md"]})
        with self.assertRaises(mechanical.AuditError):
            mechanical.run(build({"A.txt": "x"}), {"name": "t", "include": ["**/*.md"]})

    def test_malformed_profile_file_is_an_error(self):
        d = build({"p.json": '{"name": "x",,}', "A.md": "x"})
        self.assertEqual(quiet(mechanical.main, [d, "--profile", os.path.join(d, "p.json"), "--out", os.path.join(d, "o")]), 2)

    def test_disabled_checks_are_visible(self):
        d = build({"A.md": "# a\n"})
        _, rep = mechanical.run(d, {"name": "t", "include": ["*.md"]})
        run = rep["checks_run"]
        self.assertFalse(run["M-02"]["enabled"])
        self.assertEqual(run["M-02"]["reason"], "not configured in profile")
        self.assertFalse(run["M-03"]["enabled"])
        self.assertTrue(run["M-04"]["enabled"])
        self.assertEqual(rep["scope"]["files_in_scope"], 1)

    def test_exit_codes(self):
        d = build({"A.md": GOOD.replace(ANCHOR, "x"), "B.md": GOOD, "Other.md": "x"})
        pf = os.path.join(d, "p.json")
        out = os.path.join(d, "o")
        dump(pf, dict(PROFILE, include=["A.md"]))
        self.assertEqual(quiet(mechanical.main, [d, "--profile", pf, "--out", out]), 1)
        dump(pf, dict(PROFILE, include=["B.md"], required_sections=["## Missing"]))
        self.assertEqual(quiet(mechanical.main, [d, "--profile", pf, "--out", out]), 3)
        dump(pf, dict(PROFILE, include=["B.md"]))
        self.assertEqual(quiet(mechanical.main, [d, "--profile", pf, "--out", out]), 0)


@unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
class Symlinks(unittest.TestCase):
    def test_symlinks_are_not_followed_or_hashed(self):
        outside = build({"secret.md": "SECRET\n"})
        d = build({"A.md": "# a\n"})
        try:
            os.symlink(os.path.join(outside, "secret.md"), os.path.join(d, "link.md"))
            os.symlink(outside, os.path.join(d, "linkdir"))
        except OSError:
            self.skipTest("cannot create symlinks here")
        m, rep = mechanical.run(d, {"name": "t", "include": ["**/*.md"]})
        self.assertEqual([f["path"] for f in m["files"]], ["A.md"])
        self.assertEqual(sorted(rep["scope"]["symlinks_skipped"]), ["link.md", "linkdir/secret.md"])
        self.assertEqual(len(checks(rep, "M-07")), 2)
        self.assertNotIn("SECRET", json.dumps(m) + json.dumps(rep))


class Profiles(unittest.TestCase):
    def test_non_lazarusforge_fixture(self):
        repo = os.path.join(HERE, "fixtures", "generic_repo")
        _, rep = mechanical.run(repo, mechanical.load_profile(os.path.join(ROOT, "profiles", "generic_docs.json")))
        got = {(f["check"], f["severity"]) for f in rep["findings"]}
        self.assertEqual(got, {("M-04", "major"), ("M-04", "minor"), ("M-05", "major"), ("M-05", "minor")})
        self.assertEqual(mechanical.exit_code(rep), 3)
        self.assertFalse(rep["checks_run"]["M-02"]["enabled"])

    def test_every_shipped_profile_loads(self):
        pdir = os.path.join(ROOT, "profiles")
        names = [n for n in os.listdir(pdir) if n.endswith(".json")]
        self.assertGreaterEqual(len(names), 3)
        for n in names:
            mechanical.load_profile(os.path.join(pdir, n))

    def test_auditbot_audits_itself_without_critical_findings(self):
        _, rep = mechanical.run(ROOT, mechanical.load_profile(os.path.join(ROOT, "profiles", "auditbot_self.json")))
        self.assertEqual(rep["counts"]["critical"], 0)
        self.assertEqual(rep["counts"]["major"], 0)


if __name__ == "__main__":
    unittest.main()
