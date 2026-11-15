# AuditBot phase 1 in Google Colab. Paste into one cell and run.
# 1) Upload the AuditBot folder (or zip) and the target repo zip to /content, or edit the paths below.
import glob, os, sys, zipfile

TARGET_ZIP = "/content/target.zip"          # the repo you are auditing
AUDITBOT_DIR = "/content/AuditBot"          # folder containing tools/ and profiles/
PROFILE = "lazarusforge.json"
OUT = "/content/audit_out"

if os.path.exists(TARGET_ZIP):
    zipfile.ZipFile(TARGET_ZIP).extractall("/content/target")
roots = [os.path.dirname(p) for p in glob.glob("/content/target/**/Routing.md", recursive=True)]
TARGET = roots[0] if roots else "/content/target"   # any tree root; edit if your target has no Routing.md
print("target:", TARGET)

sys.path.insert(0, os.path.join(AUDITBOT_DIR, "tools"))
import mechanical
rc = mechanical.main([TARGET, "--profile", os.path.join(AUDITBOT_DIR, "profiles", PROFILE), "--out", OUT])
print("exit code:", rc, "| results in", OUT, "(manifest.json, findings.json)")
