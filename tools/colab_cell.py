# AuditBot in Google Colab. Paste into one cell and run.
# 1) Upload the AuditBot folder to /content/AuditBot and the target repo zip to /content/target.zip.
# 2) Set TARGET_ROOT to the folder inside the unzipped target that you want audited. No guessing.
import os, sys, zipfile

AUDITBOT_DIR = "/content/AuditBot"
TARGET_ZIP = "/content/target.zip"        # leave as is if the target is already unpacked
TARGET_ROOT = "/content/target"           # the exact folder to audit, e.g. /content/target/MyRepo-1.0
PROFILE = "generic_docs.json"             # or lazarusforge.json, or your own in profiles/
OUT = "/content/audit_out"

if os.path.exists(TARGET_ZIP):
    zipfile.ZipFile(TARGET_ZIP).extractall("/content/target")
if not os.path.isdir(TARGET_ROOT):
    raise SystemExit("TARGET_ROOT does not exist: %s" % TARGET_ROOT)
print("auditing:", TARGET_ROOT, "| top level:", sorted(os.listdir(TARGET_ROOT))[:12])

sys.path.insert(0, os.path.join(AUDITBOT_DIR, "tools"))
import mechanical
rc = mechanical.main([TARGET_ROOT, "--profile", os.path.join(AUDITBOT_DIR, "profiles", PROFILE), "--out", OUT])
print("exit code:", rc, "(0 clean, 1 critical, 2 error, 3 major) | results in", OUT)

# After phases 2 and 3, save their findings as JSON and verify the citations:
#   import verify_findings
#   verify_findings.main([TARGET_ROOT, "--manifest", OUT + "/manifest.json",
#                         "--findings", "/content/p2_findings.json", "--out", OUT + "/verification.json"])
